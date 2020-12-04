"""Connect to and read data from the database.


A number of functions are adapted from the Solar Forecast Arbiter with
the following license:

MIT License

Copyright (c) 2018 SolarArbiter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
from contextlib import contextmanager
import datetime as dt
from functools import partial
import json
from typing import List
from uuid import UUID


from fastapi import Depends, HTTPException
import pandas as pd
import pymysql
from pymysql import converters
import pytz
from sqlalchemy.engine import create_engine
from sqlalchemy.pool import QueuePool


from . import settings, models
from .auth import get_user_id


# this is faster than using strftime
TIMEFORMAT = "'{0.year:04}-{0.month:02}-{0.day:02} {0.hour:02}:{0.minute:02}:{0.second:02}'"  # NOQA


def escape_timestamp(value, mapping=None):
    # adapted from the SolarForecastArbiter API under the above MIT license
    if value.tzinfo is not None:
        return TIMEFORMAT.format(value.tz_convert("UTC"))
    else:
        return TIMEFORMAT.format(value)


def escape_datetime(value, mapping=None):
    # adapted from the SolarForecastArbiter API under the above MIT license
    if value.tzinfo is not None:
        return TIMEFORMAT.format(value.astimezone(dt.timezone.utc))
    else:
        return TIMEFORMAT.format(value)


def convert_datetime_utc(obj):
    # adapted from the SolarForecastArbiter API under the above MIT license
    unlocalized = converters.convert_datetime(obj)
    return pytz.utc.localize(unlocalized)


def _make_sql_connection_partial(
    host=None, port=None, user=None, password=None, database=None
):
    # adapted from the SolarForecastArbiter API under the above MIT license
    conv = converters.conversions.copy()
    # either convert decimals to floats, or add decimals to schema
    conv[converters.FIELD_TYPE.DECIMAL] = float
    conv[converters.FIELD_TYPE.NEWDECIMAL] = float
    conv[converters.FIELD_TYPE.TIMESTAMP] = convert_datetime_utc
    conv[converters.FIELD_TYPE.DATETIME] = convert_datetime_utc
    conv[converters.FIELD_TYPE.JSON] = json.loads
    conv[UUID] = converters.escape_str
    conv[pd.Timestamp] = escape_timestamp
    conv[dt.datetime] = escape_datetime
    connect_kwargs = {
        "host": host or settings.mysql_host,
        "port": port or settings.mysql_port,
        "user": user or settings.mysql_user,
        "password": password or settings.mysql_password,
        "database": database or settings.mysql_database,
        "binary_prefix": True,
        "conv": conv,
        "use_unicode": True,
        "charset": "utf8mb4",
        "init_command": "SET time_zone = '+00:00'",
    }
    if settings.mysql_use_ssl:
        connect_kwargs["ssl"] = {"ssl": True}
    getconn = partial(pymysql.connect, **connect_kwargs)
    return getconn


engine = create_engine(
    "mysql+pymysql://",
    creator=_make_sql_connection_partial(),
    poolclass=QueuePool,
    pool_recycle=3600,
    pool_pre_ping=True,
).pool


class StorageInterface:
    def __init__(self, user: str = Depends(get_user_id)):
        self.user = user
        self._cursor = None
        self.commit = True

    @property
    def cursor(self):
        if self._cursor is None:
            raise AttributeError("Cursor is only available within `start_transaction`")
        return self._cursor

    @contextmanager
    def start_transaction(self):
        connection = engine.connect()
        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
        self._cursor = cursor
        try:
            yield self
        except Exception:
            connection.rollback()
            raise
        else:
            if self.commit:
                connection.commit()
        finally:
            connection.close()
        self._cursor = None

    def try_query(self, query, args):
        # adapted from the SolarForecastArbiter API under the above MIT license
        try:
            self.cursor.execute(query, args)
        except (
            pymysql.err.OperationalError,
            pymysql.err.IntegrityError,
            pymysql.err.InternalError,
            pymysql.err.DataError,
        ) as err:
            ecode = err.args[0]
            msg = err.args[1]
            if ecode == 1142:
                raise HTTPException(status_code=404, detail=msg)
            elif ecode == 1062:
                raise HTTPException(status_code=409)
            elif ecode == 3140 or ecode == 1406 or ecode == 1048:
                raise HTTPException(status_code=400, detail=msg)
            else:
                raise

    def _call_procedure(
        self,
        procedure_name: str,
        *args,
        with_current_user: bool = True,
    ) -> dict:
        """
        Can't user callproc since it doesn't properly use converters.
        Will not handle OUT or INOUT parameters without first setting
        local variables and retrieving from those variables
        """
        # adapted from the SolarForecastArbiter API under the above MIT license
        if with_current_user:
            new_args = (self.user, *args)
        else:
            new_args = args
        query = f'CALL {procedure_name}({",".join(["%s"] * len(new_args))})'
        self.try_query(query, new_args)
        return self.cursor.fetchall()

    def _call_procedure_for_single(
        self,
        procedure_name: str,
        *args,
        with_current_user: bool = True,
    ) -> dict:
        """Wrapper handling try/except logic when a single value is expected"""
        # adapted from the SolarForecastArbiter API under the above MIT license
        try:
            result = self._call_procedure(
                procedure_name,
                *args,
                with_current_user=with_current_user,
            )[0]
        except IndexError:
            raise HTTPException(status_code=404)
        return result

    def ensure_user_exists(self) -> str:
        return self._call_procedure_for_single("create_user_if_not_exists")["user_id"]

    def list_systems(self) -> List[models.StoredPVSystem]:
        systems = self._call_procedure("list_systems")
        out = []
        for sys in systems:
            sys["object_id"] = sys.pop("system_id")
            sys["object_type"] = "system"
            out.append(models.StoredPVSystem(**sys))
        return out

    def create_system(self, system_def: models.PVSystem) -> models.StoredObjectID:
        created = self._call_procedure_for_single(
            "create_system", system_def.name, system_def.json()
        )
        return models.StoredObjectID(
            object_id=created["system_id"], object_type="system"
        )

    def get_system(self, system_id: UUID) -> models.StoredPVSystem:
        system = self._call_procedure_for_single("get_system", system_id)
        system["object_id"] = system.pop("system_id")
        system["object_type"] = "system"
        return models.StoredPVSystem(**system)

    def delete_system(self, system_id: UUID):
        self._call_procedure("delete_system", system_id)

    def update_system(
        self, system_id: UUID, system_def: models.PVSystem
    ) -> models.StoredObjectID:
        self._call_procedure("update_system", system_id, system_def.json())
        return models.StoredObjectID(object_id=system_id, object_type="system")


def ensure_user(storage: StorageInterface = Depends(StorageInterface)):
    with storage.start_transaction() as st:
        st.ensure_user_exists()

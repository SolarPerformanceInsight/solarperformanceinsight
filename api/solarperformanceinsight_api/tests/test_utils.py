import datetime as dt
from functools import partial
from io import BytesIO, StringIO


from fastapi import HTTPException
import numpy as np
import pandas as pd
import pyarrow as pa
from pyarrow import feather
import pytest


from solarperformanceinsight_api import utils, models


httpfail = partial(
    pytest.param, marks=pytest.mark.xfail(strict=True, raises=HTTPException)
)


@pytest.mark.parametrize(
    "inp,typ,exp",
    (
        (
            "time,datas\n2020-01-01T00:00Z,8.9",
            StringIO,
            pd.DataFrame({"time": [pd.Timestamp("2020-01-01T00:00Z")], "datas": [8.9]}),
        ),
        (
            b"time,datas\n2020-01-01T00:00Z,8.9",
            BytesIO,
            pd.DataFrame({"time": [pd.Timestamp("2020-01-01T00:00Z")], "datas": [8.9]}),
        ),
        (
            b"time,datas\n2020-01-01T00:00,8.9\n2020-01-02T00:00,-999",
            BytesIO,
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2020-01-01T00:00"),
                        pd.Timestamp("2020-01-02T00:00"),
                    ],
                    "datas": [8.9, None],
                }
            ),
        ),
        # not valid later, but rely on dataframe validation to check dtypes
        (
            b"multi,header\ntime,datas\n2020-01-01T00:00,8.9\n2020-01-02T00:00,-999",
            BytesIO,
            pd.DataFrame(
                {
                    "multi": ["time", "2020-01-01T00:00", "2020-01-02T00:00"],
                    "header": ["datas", "8.9", np.nan],
                }
            ),
        ),
        # no header row
        httpfail(
            b"2020-01-01T00:00,8.9\n2020-01-02T00:00,-999",
            BytesIO,
            None,
        ),
        httpfail(
            "",
            StringIO,
            None,
        ),
        httpfail(
            "empty",
            StringIO,
            None,
        ),
        httpfail(
            "notenoughheaders,\na,b",
            StringIO,
            None,
        ),
        httpfail(
            "a,b\n0,1,2\n0,1,3,4,5,6",
            StringIO,
            None,
        ),
    ),
)
def test_read_csv(inp, typ, exp):
    out = utils.read_csv(typ(inp))
    pd.testing.assert_frame_equal(out, exp)


@pytest.mark.parametrize(
    "tbl,exp",
    (
        (
            pa.Table.from_arrays([[1.0, 2, 3], [4.0, 5, 6]], ["a", "b"]),
            pd.DataFrame({"a": [1, 2, 3.0], "b": [4, 5, 6.0]}),
        ),
        # complex types to test to_pandas
        (
            pa.Table.from_arrays(
                [pa.array([1.0, 2, 3]), pa.array([[], [5, 6], [7, 8]])], ["a", "b"]
            ),
            pd.DataFrame({"a": [1, 2, 3.0], "b": [[], [5, 6], [7, 8]]}),
        ),
        httpfail(
            b"notanarrowfile",
            None,
        ),
    ),
)
def test_read_arrow(tbl, exp):
    if isinstance(tbl, bytes):
        tblbytes = BytesIO(tbl)
    else:
        tblbytes = BytesIO(utils.dump_arrow_bytes(tbl))
    out = utils.read_arrow(tblbytes)
    pd.testing.assert_frame_equal(out, exp)


@pytest.mark.parametrize(
    "inp,exp",
    (
        ("text/csv", utils.read_csv),
        ("application/vnd.ms-excel", utils.read_csv),
        ("application/vnd.apache.arrow.file", utils.read_arrow),
        ("application/octet-stream", utils.read_arrow),
        httpfail("application/json", None),
    ),
)
def test_verify_content_type(inp, exp):
    out = utils.verify_content_type(inp)
    assert out == exp


@pytest.mark.parametrize(
    "inp,cols,exp",
    (
        (pd.DataFrame({"a": [0, 1], "b": [1, 2]}), ["a", "b"], set()),
        (
            pd.DataFrame(
                {"time": [pd.Timestamp("2020-01-01")], "b": [0.8], "c": ["notnumeric"]}
            ),
            ["time", "b"],
            {"c"},
        ),
        httpfail(
            pd.DataFrame({"time": [pd.Timestamp("2020-01-01")], "b": ["willfail"]}),
            ["time", "b"],
            set(),
        ),
        httpfail(pd.DataFrame({"a": [0, 1], "b": [1, 2]}), ["c"], {"a", "b"}),
        httpfail(pd.DataFrame({"time": [0, 1], "b": [1, 2]}), ["time", "b"], set()),
        (
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp.now(),
                        pd.Timestamp("2020-01-01T00:00:01.09230"),
                    ],
                    "b": [1, 2],
                }
            ),
            ["time", "b"],
            set(),
        ),
        httpfail(
            pd.DataFrame(
                {
                    "time": [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-01")],
                    "b": [0.8, 1],
                },
            ),
            ["time", "b"],
            set(),
        ),
    ),
)
def test_validate_dataframe(inp, cols, exp):
    out = utils.validate_dataframe(inp, cols)
    assert out == exp


@pytest.mark.parametrize(
    "df,tbl",
    (
        (
            pd.DataFrame({"a": [0.1, 0.2]}, dtype="float64"),
            pa.Table.from_arrays(
                [pa.array([0.1, 0.2], type=pa.float32())], names=["a"]
            ),
        ),
        (
            pd.DataFrame({"a": [0.1, 0.2]}, dtype="float32"),
            pa.Table.from_arrays(
                [pa.array([0.1, 0.2], type=pa.float32())], names=["a"]
            ),
        ),
        (
            pd.DataFrame(
                {
                    "a": [0.1, 0.2],
                    "time": [
                        pd.Timestamp("2020-01-01T00:00Z"),
                        pd.Timestamp("2020-01-02T00:00Z"),
                    ],
                },
            ),
            pa.Table.from_arrays(
                [
                    pa.array([0.1, 0.2], type=pa.float32()),
                    pa.array(
                        [
                            dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
                            dt.datetime(2020, 1, 2, tzinfo=dt.timezone.utc),
                        ],
                        type=pa.timestamp("s", tz="UTC"),
                    ),
                ],
                names=["a", "time"],
            ),
        ),
        (
            pd.DataFrame(
                {
                    "b": [-999, 129],
                    "time": [
                        pd.Timestamp("2020-01-01T00:00Z"),
                        pd.Timestamp("2020-01-02T00:00Z"),
                    ],
                    "a": [0.1, 0.2],
                },
            ),
            pa.Table.from_arrays(
                [
                    pa.array([-999, 129], type=pa.int64()),
                    pa.array(
                        [
                            dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
                            dt.datetime(2020, 1, 2, tzinfo=dt.timezone.utc),
                        ],
                        type=pa.timestamp("s", tz="UTC"),
                    ),
                    pa.array([0.1, 0.2], type=pa.float32()),
                ],
                names=["b", "time", "a"],
            ),
        ),
        (
            pd.DataFrame(
                {"a": [0.1, 0.2], "time": ["one", "two"]},
            ),
            pa.Table.from_arrays(
                [
                    pa.array([0.1, 0.2], type=pa.float32()),
                    pa.array(["one", "two"]),
                ],
                names=["a", "time"],
            ),
        ),
        # non-localized ok
        (
            pd.DataFrame(
                {
                    "b": [-999, 129],
                    "time": [
                        pd.Timestamp("2020-01-01T00:00"),
                        pd.Timestamp("2020-01-02T00:00"),
                    ],
                    "a": [0.1, 0.2],
                },
            ),
            pa.Table.from_arrays(
                [
                    pa.array([-999, 129], type=pa.int64()),
                    pa.array(
                        [
                            dt.datetime(2020, 1, 1),
                            dt.datetime(2020, 1, 2),
                        ],
                        type=pa.timestamp("s"),
                    ),
                    pa.array([0.1, 0.2], type=pa.float32()),
                ],
                names=["b", "time", "a"],
            ),
        ),
        (
            pd.DataFrame(
                {"nanfloat": [None, 1.0], "nans": [pd.NA, pd.NA], "str": ["a", "b"]}
            ),
            pa.Table.from_arrays(
                [
                    pa.array([None, 1.0], type=pa.float32()),
                    pa.array([None, None], type=pa.null()),
                    pa.array(["a", "b"], type=pa.string()),
                ],
                names=["nanfloat", "nans", "str"],
            ),
        ),
        httpfail(
            pd.DataFrame(
                {
                    "nanint": [pd.NA, 3],  # arrow doesn't like this
                }
            ),
            None,
        ),
        httpfail(
            pd.DataFrame(
                {
                    "nanstr": [pd.NA, "string"],
                }
            ),
            None,
        ),
    ),
)
def test_convert_to_arrow(df, tbl):
    out = utils.convert_to_arrow(df)
    assert out == tbl


@pytest.mark.parametrize(
    "df",
    (
        pd.DataFrame(),
        pd.DataFrame({"a": [0, 1992.9]}),
        pd.DataFrame(
            {
                "b": [-999, 129],
                "time": [
                    pd.Timestamp("2020-01-01T00:00"),
                    pd.Timestamp("2020-01-02T00:00"),
                ],
                "a": [0.1, 0.2],
            },
        ),
        pd.DataFrame(
            {
                "b": [-999, 129],
                "time": [
                    pd.Timestamp("2020-01-01T00:00Z"),
                    pd.Timestamp("2020-01-02T00:00Z"),
                ],
                "a": [0.1, 0.2],
            },
        ),
    ),
)
def test_dump_arrow_bytes(df):
    tbl = pa.Table.from_pandas(df)
    out = utils.dump_arrow_bytes(tbl)
    assert isinstance(out, bytes)
    new = feather.read_feather(BytesIO(out))
    pd.testing.assert_frame_equal(df, new)


@pytest.mark.parametrize(
    "inp,jti,exp_df,exp_extra,exp_missing",
    [
        (
            pd.DataFrame(
                {
                    "time": pd.date_range(
                        start="2020-01-01T00:00Z", freq="5min", periods=10
                    ),
                    "col0": [0, 1, 2, 3, 4.0, 5, 6, 7, 8, 9],
                }
            ),
            {
                "start": "2020-01-01T00:00Z",
                "end": "2020-01-01T00:50Z",
                "step": "05:00",
                "timezone": None,
            },
            pd.DataFrame(
                {
                    "time": pd.date_range(
                        start="2020-01-01T00:00Z", freq="5min", periods=10
                    ),
                    "col0": [0, 1, 2, 3, 4.0, 5, 6, 7, 8, 9],
                }
            ),
            [],
            [],
        ),
        (
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2020-01-01T00:00:00.00877Z"),
                        pd.Timestamp("2020-01-01T00:14:59.9871Z"),
                        pd.Timestamp("2020-01-01T00:30Z"),
                        pd.Timestamp("2020-01-01T00:45Z"),
                    ],
                    "col0": [0, 1, 2, 3.0],
                }
            ),
            {
                "start": "2020-01-01T00:00Z",
                "end": "2020-01-01T00:50Z",
                "step": "15:00",
                "timezone": None,
            },
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2020-01-01T00:00Z"),
                        pd.Timestamp("2020-01-01T00:15Z"),
                        pd.Timestamp("2020-01-01T00:30Z"),
                        pd.Timestamp("2020-01-01T00:45Z"),
                    ],
                    "col0": [0, 1, 2, 3.0],
                }
            ),
            [],
            [],
        ),
        (
            pd.DataFrame(
                {
                    "time": pd.date_range(
                        start="2020-01-01T00:00Z", freq="5min", periods=10
                    ),
                    "col0": [0, 1, 2, 3, 4.0, 5, 6, 7, 8, 9],
                }
            ),
            {
                "start": "2020-01-01T00:00Z",
                "end": "2020-01-01T00:45Z",
                "step": "05:00",
                "timezone": None,
            },
            pd.DataFrame(
                {
                    "time": pd.date_range(
                        start="2020-01-01T00:00Z", freq="5min", periods=9
                    ),
                    "col0": [0, 1, 2, 3, 4.0, 5, 6, 7, 8],
                }
            ),
            [pd.Timestamp("2020-01-01T00:45Z")],
            [],
        ),
        (
            pd.DataFrame({"time": [pd.Timestamp("2020-01-01T00:15Z")], "other": [0.0]}),
            {
                "start": "2020-01-01T00:00Z",
                "end": "2020-01-01T01:00Z",
                "step": "15:00",
                "timezone": "UTC",
            },
            pd.DataFrame(
                {
                    "time": pd.date_range(
                        start="2020-01-01T00:00Z", freq="15min", periods=4
                    ),
                    "other": [np.nan, 0.0, np.nan, np.nan],
                }
            ),
            [],
            [
                pd.Timestamp("2020-01-01T00:00Z"),
                pd.Timestamp("2020-01-01T00:30Z"),
                pd.Timestamp("2020-01-01T00:45Z"),
            ],
        ),
        (
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2020-01-01T00:15"),
                        pd.Timestamp("2020-01-01T01:00"),
                    ],
                    "other": [0.0, 1.0],
                }
            ),
            {
                "start": "2020-01-01T00:00",
                "end": "2020-01-01T01:00",
                "step": "15:00",
                "timezone": "UTC",
            },
            pd.DataFrame(
                {
                    "time": pd.date_range(
                        start="2020-01-01T00:00Z", freq="15min", periods=4
                    ),
                    "other": [np.nan, 0.0, np.nan, np.nan],
                }
            ),
            [pd.Timestamp("2020-01-01T01:00Z")],
            [
                pd.Timestamp("2020-01-01T00:00Z"),
                pd.Timestamp("2020-01-01T00:30Z"),
                pd.Timestamp("2020-01-01T00:45Z"),
            ],
        ),
    ],
)
def test_reindex_timeseries(inp, jti, exp_df, exp_extra, exp_missing):
    new, extra, missing = utils.reindex_timeseries(inp, models.JobTimeindex(**jti))
    pd.testing.assert_frame_equal(new, exp_df)
    assert extra == exp_extra
    assert missing == exp_missing

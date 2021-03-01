import calendar
import datetime as dt
import logging
from typing import Set, IO, Callable, List, Tuple


from fastapi import HTTPException
import pandas as pd
from pandas.errors import EmptyDataError, ParserError  # type: ignore
import pandas.api.types as pdtypes  # type: ignore
import pyarrow as pa  # type: ignore


from . import models


logger = logging.getLogger(__name__)


def read_csv(content: IO) -> pd.DataFrame:
    """Read a CSV into a DataFrame"""
    kwargs = dict(
        na_values=[-999.0, -9999.0],
        keep_default_na=True,
        comment="#",
        header=0,
        skip_blank_lines=True,
    )
    # read headers first to see if a "time" column is present
    try:
        head_df = pd.read_csv(content, nrows=0, **kwargs)  # type: ignore
    except (EmptyDataError, ParserError) as err:
        raise HTTPException(status_code=400, detail=err.args[0])
    for i, header in enumerate(head_df.columns):
        try:
            float(header)
        except ValueError:
            pass
        else:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"The header '{header}' can be parsed as a "
                    "float indicating a header row may be missing?"
                ),
            )
        if len(header) == 0 or header.startswith("Unnamed:"):
            raise HTTPException(status_code=400, detail=f"Empty header for column {i}")

    if "time" in head_df.columns:
        kwargs["parse_dates"] = ["time"]
    content.seek(0)
    try:
        df = pd.read_csv(content, **kwargs)  # type: ignore
    except (EmptyDataError, ParserError) as err:
        raise HTTPException(status_code=400, detail=err.args[0])
    if df.empty:
        raise HTTPException(status_code=400, detail="Empty CSV file")
    return df


def read_arrow(content: IO) -> pd.DataFrame:
    """Read a buffer in Apache Arrow File format into a DataFrame"""
    try:
        table = pa.ipc.open_file(content).read_all()
    except pa.lib.ArrowInvalid as err:
        raise HTTPException(status_code=400, detail=err.args[0])
    df = table.to_pandas(split_blocks=True)
    return df


def verify_content_type(content_type: str) -> Callable[[IO], pd.DataFrame]:
    """Checks if we can read the content_type and returns the appropriate function for
    reading"""
    csv_types = ("text/csv", "application/vnd.ms-excel")
    arrow_types = (
        "application/octet-stream",
        "application/vnd.apache.arrow.file",
    )
    # reject non csv/arrow
    if content_type not in csv_types and content_type not in arrow_types:
        raise HTTPException(
            status_code=415,
            detail=(
                "Acceptable formats are CSV (text/csv) and the Apache Arrow "
                "file format (application/vnd.apache.arrow.file)"
            ),
        )
    if content_type in csv_types:
        return read_csv
    else:
        return read_arrow


MONTH_MAPPING = dict(
    zip(
        list(calendar.month_abbr[1:])
        + [m + "." for m in calendar.month_abbr[1:]]
        + list(calendar.month_name[1:])
        + [m.lower() for m in calendar.month_abbr[1:]]
        + [m.lower() + "." for m in calendar.month_abbr[1:]]
        + [m.lower() for m in calendar.month_name[1:]]
        + list(range(1, 13))  # type: ignore
        + [float(i) for i in range(1, 13)]  # type: ignore
        + [str(i) for i in range(1, 13)]
        + [f"{i}." for i in range(1, 13)]
        + [f"{i}.0" for i in range(1, 13)],
        list(calendar.month_name[1:]) * 11,
    )
)


def validate_dataframe(df: pd.DataFrame, columns: List[str]) -> Set[str]:
    """Validates that the input dataframe has all given columns, that the
    'time' column has a datetime type, a 'month' column parsed as 1-12 or Jan-Dec,
    and that all other columns are floats.
    """
    expected = set(columns)
    actual = set(df.columns)
    diff = expected - actual
    if len(diff) > 0:
        raise HTTPException(
            status_code=400, detail="Data is missing column(s) " + ", ".join(diff)
        )
    if "time" in expected:
        if not pdtypes.is_datetime64_any_dtype(df["time"]):
            raise HTTPException(
                status_code=400,
                detail='"time" column could not be parsed as a timestamp',
            )
        # check for duplicates
        extra_times = len(df["time"]) - len(df["time"].unique())
        if extra_times != 0:
            raise HTTPException(
                status_code=400,
                detail=f'"time" column has {extra_times} duplicate entries',
            )
    if "month" in expected:
        if len(df["month"]) != 12:
            raise HTTPException(
                status_code=400,
                detail='"month" column is expected to have 12 rows, one for each month',
            )
        allowed = set(MONTH_MAPPING.keys())
        month_set = set(df["month"])
        invalid_months = len(month_set - allowed)
        if invalid_months:
            raise HTTPException(
                status_code=400,
                detail=(
                    f'"month" column has {invalid_months} rows that could not be parsed'
                ),
            )

    bad_types = []
    for col in expected - {"time", "month"}:
        if not pdtypes.is_numeric_dtype(df[col]):
            bad_types.append(col)
    if bad_types:
        raise HTTPException(
            status_code=400,
            detail="The following column(s) are not numeric: " + ", ".join(bad_types),
        )
    return actual - expected


def standardize_months(df: pd.DataFrame) -> pd.DataFrame:
    newdf: pd.DataFrame
    newdf = df.copy()
    newdf.loc[:, "month"] = newdf["month"].map(MONTH_MAPPING)
    return newdf


def reindex_timeseries(
    df: pd.DataFrame, jobtimeindex: models.JobTimeindex, allow_time_shift: bool = False
) -> Tuple[pd.DataFrame, List[dt.datetime], List[dt.datetime]]:
    """Conforms a dataframe to the expected time index for a job"""
    # some annoying type behaviour
    newdf: pd.DataFrame
    newdf = df.copy().sort_values("time")
    time_kwargs = dict(ambiguous=True, nonexistent="NaT")
    index = pd.DatetimeIndex(newdf.pop("time")).round(  # type: ignore
        "1s", **time_kwargs.copy()
    )
    if index.tzinfo is None:
        index = index.tz_localize(jobtimeindex.timezone, **time_kwargs.copy())
    else:
        index = index.tz_convert(jobtimeindex.timezone)
    if allow_time_shift:
        # shift start year of index to match year of job start
        ref_yr = index[0].year
        job_yr = jobtimeindex._time_range[0].year
        if ref_yr != job_yr:
            shift = pd.DateOffset(years=job_yr - ref_yr)  # type: ignore
            # pandas#28610 means we can't just use newdf.shift
            index = (shift + index.tz_localize(None)).tz_localize(
                index.tz, **time_kwargs.copy()
            )

    if not index.equals(jobtimeindex._time_range):
        extra = list(
            index.dropna().difference(jobtimeindex._time_range).to_pydatetime()
        )
        missing = list(
            jobtimeindex._time_range.difference(  # type: ignore
                index.dropna()
            ).to_pydatetime()
        )
    else:
        extra = []
        missing = []
    newdf.index = index
    # drop possible duplicate feb 28 when going from leap year to non
    # and possible duplicate times from DST transitions
    newdf = newdf.loc[~(newdf.index.duplicated() | newdf.index.isna())]
    newdf = newdf.reindex(jobtimeindex._time_range, copy=False)  # type: ignore
    newdf.index.name = "time"  # type: ignore
    newdf.reset_index(inplace=True)  # type: ignore
    return newdf, extra, missing


def _map_pandas_val_to_arrow_dtypes(ser: pd.Series) -> pa.DataType:
    # save on storage w/ second precisison timestamps and float32
    dtype = ser.dtype  # type: ignore
    if pdtypes.is_datetime64_any_dtype(dtype):
        return pa.timestamp("s", tz=getattr(dtype, "tz", None))
    elif pdtypes.is_float_dtype(dtype):
        return pa.float32()
    else:
        return pa.array(ser, from_pandas=True).type


def convert_to_arrow(df: pd.DataFrame) -> pa.Table:
    """Convert a DataFrame into an Arrow Table setting datetime columns to
    have second precision, float columns to be float32, and infer other types.
    Errors are likely if the first row of a column is NA and the column isn't a
    float.
    """
    try:
        schema = pa.schema(
            (col, _map_pandas_val_to_arrow_dtypes(val))
            for col, val in df.iloc[:1].items()  # type: ignore
        )
        table = pa.Table.from_pandas(df, schema=schema)
    except pa.lib.ArrowInvalid as err:
        logger.error(err.args[0])
        raise HTTPException(status_code=400, detail=err.args[0])
    return table


def dump_arrow_bytes(table: pa.Table) -> bytes:
    """Dump an Arrow table out to bytes in the Arrow File/Feather format"""
    sink = pa.BufferOutputStream()
    writer = pa.ipc.new_file(sink, table.schema)
    writer.write(table)
    writer.close()
    return sink.getvalue().to_pybytes()

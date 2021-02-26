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
        (
            pd.DataFrame(
                {
                    "month": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    "other": list(range(12)),
                }
            ),
            ["month", "other"],
            set(),
        ),
        (
            pd.DataFrame(
                {
                    "month": [
                        1.0,
                        2.0,
                        3.0,
                        4.0,
                        5.0,
                        6.0,
                        7.0,
                        8.0,
                        9.0,
                        10.0,
                        11.0,
                        12.0,
                    ],
                    "other": list(range(12)),
                }
            ),
            ["month", "other"],
            set(),
        ),
        (
            pd.DataFrame(
                {
                    "month": [f"{i}." for i in range(1, 13)],
                    "other": list(range(12)),
                }
            ),
            ["month", "other"],
            set(),
        ),
        (
            pd.DataFrame(
                {
                    "month": [str(i) for i in range(1, 13)],
                    "other": list(range(12)),
                }
            ),
            ["month", "other"],
            set(),
        ),
        (
            pd.DataFrame(
                {
                    "month": [f"{i}.0" for i in range(1, 13)],
                    "other": list(range(12)),
                }
            ),
            ["month", "other"],
            set(),
        ),
        (
            pd.DataFrame(
                {
                    "month": [
                        "Jan",
                        "Feb",
                        "Mar",
                        "Apr",
                        "May",
                        "Jun",
                        "Jul",
                        "Aug",
                        "Sep",
                        "Oct",
                        "Nov",
                        "Dec",
                    ],
                    "other": list(range(12)),
                }
            ),
            ["month"],
            {"other"},
        ),
        (
            pd.DataFrame(
                {
                    "month": [
                        "January",
                        "February",
                        "March",
                        "April",
                        "May",
                        "June",
                        "July",
                        "August",
                        "September",
                        "October",
                        "November",
                        "December",
                    ],
                }
            ),
            ["month"],
            set(),
        ),
        (
            pd.DataFrame(
                {
                    "month": [
                        "jan.",
                        "feb.",
                        "mar.",
                        "apr.",
                        "may",
                        "jun.",
                        "jul.",
                        "aug.",
                        "sep.",
                        "oct.",
                        "nov.",
                        "dec.",
                    ],
                    "other": list(range(12)),
                }
            ),
            ["month"],
            {"other"},
        ),
        (
            pd.DataFrame(
                {
                    "month": [
                        "January",
                        "february",
                        "march",
                        "april",
                        "may",
                        "june",
                        "july",
                        "August",
                        "september",
                        "October",
                        "November",
                        "December",
                    ],
                }
            ),
            ["month"],
            set(),
        ),
        httpfail(
            pd.DataFrame(
                {
                    "month": [
                        "October",
                        "November",
                        "December",
                    ],
                }
            ),
            ["month"],
            set(),
        ),
        httpfail(
            pd.DataFrame({"month": range(0, 13)}),
            ["month"],
            set(),
        ),
        httpfail(
            pd.DataFrame(
                {
                    "month": [
                        "January",
                        "february",
                        "march",
                        "april",
                        "may",
                        "june",
                        "julio",  # bad
                        "August",
                        "september",
                        "October",
                        "November",
                        "December",
                    ],
                }
            ),
            ["month"],
            set(),
        ),
    ),
)
def test_validate_dataframe(inp, cols, exp):
    out = utils.validate_dataframe(inp, cols)
    assert out == exp


@pytest.mark.parametrize(
    "inp,slc",
    (
        (
            pd.DataFrame(
                {
                    "month": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    "other": list(range(12)),
                }
            ),
            slice(None),
        ),
        (
            pd.DataFrame(
                {
                    "month": [
                        1.0,
                        2.0,
                        3.0,
                        4.0,
                        5.0,
                        6.0,
                        7.0,
                        8.0,
                        9.0,
                        10.0,
                        11.0,
                        12.0,
                    ],
                    "other": list(range(12)),
                }
            ),
            slice(None),
        ),
        (
            pd.DataFrame(
                {
                    "month": [str(i) for i in range(1, 13)],
                    "other": list(range(12)),
                }
            ),
            slice(None),
        ),
        (
            pd.DataFrame(
                {
                    "month": [
                        "Jan",
                        "Feb",
                        "Mar",
                        "Apr",
                        "May",
                        "Jun",
                        "Jul",
                        "Aug",
                        "Sep",
                        "Oct",
                        "Nov",
                        "Dec",
                    ],
                    "other": list(range(12)),
                }
            ),
            slice(None),
        ),
        (
            pd.DataFrame(
                {
                    "month": [
                        "January",
                        "February",
                        "March",
                        "April",
                        "May",
                        "June",
                        "July",
                        "August",
                        "September",
                        "October",
                        "November",
                        "December",
                    ],
                }
            ),
            slice(None),
        ),
        (
            pd.DataFrame(
                {
                    "month": [
                        "jan.",
                        "feb.",
                        "mar.",
                        "apr.",
                        "may",
                        "jun.",
                        "jul.",
                        "aug.",
                        "sep.",
                        "oct.",
                        "nov.",
                        "dec.",
                    ],
                    "other": list(range(12)),
                }
            ),
            slice(None),
        ),
        (
            pd.DataFrame(
                {
                    "month": [
                        "January",
                        "february",
                        "march",
                        "april",
                        "may",
                        "june",
                        "july",
                        "August",
                        "september",
                        "October",
                        "November",
                        "December",
                    ],
                }
            ),
            slice(None),
        ),
        (
            pd.DataFrame(
                {
                    "month": [
                        "October",
                        "November",
                        "December",
                    ],
                },
                index=[9, 10, 11],
            ),
            slice(9, None),
        ),
    ),
)
def test_standardize_months(inp, slc):
    exp = pd.Series(
        [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
        name="month",
    )
    out = utils.standardize_months(inp)["month"]
    pd.testing.assert_series_equal(out, exp[slc])


def test_standardize_months_fail():
    out0 = utils.standardize_months(pd.DataFrame({"month": range(0, 13)}))["month"]
    assert not pd.isna(out0[1:]).any()
    assert pd.isna(out0[:1]).all()
    out1 = utils.standardize_months(
        pd.DataFrame(
            {
                "month": [
                    "January",
                    "february",
                    "march",
                    "april",
                    "may",
                    "june",
                    "julio",  # bad
                    "August",
                    "september",
                    "October",
                    "November",
                    "December",
                ],
            }
        )
    )
    pd.testing.assert_series_equal(
        out1["month"],
        pd.Series(
            [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                None,
                "August",
                "September",
                "October",
                "November",
                "December",
            ],
            name="month",
        ),
    )


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


@pytest.mark.parametrize(
    "inp,exp,jti,ats",
    [
        (
            [pd.Timestamp("2020-01-01T00:00Z"), pd.Timestamp("2020-01-01T00:15Z")],
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2020-01-01T00:00Z"),
                        pd.Timestamp("2020-01-01T00:15Z"),
                    ],
                    "other": [0, 1],
                }
            ),
            {
                "start": "2020-01-01T00:00",
                "end": "2020-01-01T00:30",
                "step": "15:00",
                "timezone": "UTC",
            },
            True,
        ),
        (
            [pd.Timestamp("2020-01-01T00:00Z"), pd.Timestamp("2020-01-01T00:15Z")],
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2020-01-01T00:00Z"),
                        pd.Timestamp("2020-01-01T00:15Z"),
                    ],
                    "other": [0, 1],
                }
            ),
            {
                "start": "2020-01-01T00:00",
                "end": "2020-01-01T00:30",
                "step": "15:00",
                "timezone": "UTC",
            },
            False,
        ),
        (
            [pd.Timestamp("2019-01-01T00:00Z"), pd.Timestamp("2019-01-01T00:15Z")],
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2020-01-01T00:00Z"),
                        pd.Timestamp("2020-01-01T00:15Z"),
                    ],
                    "other": [None, None],
                }
            ).astype(dict(other="float64")),
            {
                "start": "2020-01-01T00:00",
                "end": "2020-01-01T00:30",
                "step": "15:00",
                "timezone": "UTC",
            },
            False,
        ),
        (
            [pd.Timestamp("2019-01-01T00:00Z"), pd.Timestamp("2019-01-01T00:15Z")],
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2020-01-01T00:00Z"),
                        pd.Timestamp("2020-01-01T00:15Z"),
                    ],
                    "other": [0, 1],
                }
            ),
            {
                "start": "2020-01-01T00:00",
                "end": "2020-01-01T00:30",
                "step": "15:00",
                "timezone": "UTC",
            },
            True,
        ),
        (
            [pd.Timestamp("2020-01-01T00:00Z"), pd.Timestamp("2020-01-01T00:15Z")],
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2023-01-01T00:00Z"),
                        pd.Timestamp("2023-01-01T00:15Z"),
                    ],
                    "other": [0, 1],
                }
            ),
            {
                "start": "2023-01-01T00:00",
                "end": "2023-01-01T00:30",
                "step": "15:00",
                "timezone": "UTC",
            },
            True,
        ),
        (
            [pd.Timestamp("2020-01-01T00:00Z"), pd.Timestamp("2020-01-01T00:15Z")],
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2002-01-01T00:00Z"),
                        pd.Timestamp("2002-01-01T00:15Z"),
                    ],
                    "other": [0, 1],
                }
            ),
            {
                "start": "2002-01-01T00:00",
                "end": "2002-01-01T00:30",
                "step": "15:00",
                "timezone": "UTC",
            },
            True,
        ),
        (
            [
                pd.Timestamp("2020-12-31T23:50Z"),
                pd.Timestamp("2020-12-31T23:55Z"),
                pd.Timestamp("2021-01-01T00:00Z"),
            ],
            # since 2020 is a leap year and could cause issues
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2021-12-31T23:50Z"),
                        pd.Timestamp("2021-12-31T23:55Z"),
                        pd.Timestamp("2022-01-01T00:00Z"),
                    ],
                    "other": [0, 1, 2],
                }
            ),
            {
                "start": "2021-12-31T23:50",
                "end": "2022-01-01T00:05",
                "step": "05:00",
                "timezone": "UTC",
            },
            True,
        ),
        (
            [
                pd.Timestamp("2020-12-31T23:50Z"),
                pd.Timestamp("2021-01-01T00:00Z"),
                pd.Timestamp("2021-01-01T00:10Z"),
            ],
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2022-01-01T00:00Z"),
                        pd.Timestamp("2022-01-01T00:10Z"),
                    ],
                    "other": [float("nan"), float("nan")],
                }
            ),
            {
                "start": "2022-01-01T00:00",
                "end": "2022-01-01T00:15",
                "step": "10:00",
                "timezone": "UTC",
            },
            True,
        ),
        (
            [
                pd.Timestamp("2020-03-31T23:50Z"),
                pd.Timestamp("2020-04-01T00:00Z"),
                pd.Timestamp("2020-04-01T00:10Z"),
            ],
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2022-01-01T00:00Z"),
                        pd.Timestamp("2022-01-01T00:10Z"),
                    ],
                    "other": [float("nan"), float("nan")],
                }
            ),
            {
                "start": "2022-01-01T00:00",
                "end": "2022-01-01T00:15",
                "step": "10:00",
                "timezone": "UTC",
            },
            True,
        ),
        (
            # in this case 2/29/2020 in ref -> 2/28/2022
            [
                pd.Timestamp("2020-02-29T23:50-07:00"),
                pd.Timestamp("2020-03-01T00:00-07:00"),
                pd.Timestamp("2020-03-01T00:10-07:00"),
            ],
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2022-02-28T23:50", tz="Etc/GMT+7"),
                        pd.Timestamp("2022-03-01T00:00", tz="Etc/GMT+7"),
                        pd.Timestamp("2022-03-01T00:10", tz="Etc/GMT+7"),
                    ],
                    "other": [0, 1, 2],
                }
            ),
            {
                "start": "2022-02-28T23:50",
                "end": "2022-03-01T00:15",
                "step": "10:00",
                "timezone": "Etc/GMT+7",
            },
            True,
        ),
        (
            # in this case 2/29/2020 in ref -> 2/29/2024
            [
                pd.Timestamp("2020-02-29T23:50-07:00"),
                pd.Timestamp("2020-03-01T00:00-07:00"),
                pd.Timestamp("2020-03-01T00:10-07:00"),
            ],
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2024-02-29T23:50", tz="Etc/GMT+7"),
                        pd.Timestamp("2024-03-01T00:00", tz="Etc/GMT+7"),
                        pd.Timestamp("2024-03-01T00:10", tz="Etc/GMT+7"),
                    ],
                    "other": [0, 1, 2],
                }
            ),
            {
                "start": "2024-02-29T23:50",
                "end": "2024-03-01T00:15",
                "step": "10:00",
                "timezone": "Etc/GMT+7",
            },
            True,
        ),
        (
            # in this case 2/29/2020 empty
            [
                pd.Timestamp("2021-02-28T23:50-07:00"),
                pd.Timestamp("2021-03-01T00:00-07:00"),
                pd.Timestamp("2021-03-01T00:10-07:00"),
            ],
            pd.DataFrame(
                {
                    "time": [
                        pd.Timestamp("2020-02-29T23:50", tz="Etc/GMT+7"),
                        pd.Timestamp("2020-03-01T00:00", tz="Etc/GMT+7"),
                        pd.Timestamp("2020-03-01T00:10", tz="Etc/GMT+7"),
                    ],
                    "other": [float("nan"), 1, 2],
                }
            ),
            {
                "start": "2020-02-29T23:50",
                "end": "2020-03-01T00:15",
                "step": "10:00",
                "timezone": "Etc/GMT+7",
            },
            True,
        ),
        (
            # in this case 2/29/2020 data is dropped
            pd.date_range(
                "2020-02-28T12:00:00Z", end="2020-03-01T12:00:00Z", freq="1h"
            ),
            pd.DataFrame(
                {
                    "time": pd.date_range(
                        "2021-02-28T12:00:00Z", end="2021-03-01T11:59:00Z", freq="1h"
                    ),
                    "other": list(range(12)) + list(range(36, 48)),
                }
            ),
            {
                "start": "2021-02-28T12:00",
                "end": "2021-03-01T12:00",
                "step": "60:00",
                "timezone": "UTC",
            },
            True,
        ),
        (
            # in this case 2/29/2020 data is dropped, test sorting too
            pd.date_range(
                "2020-02-28T12:00:00Z", end="2020-03-01T12:00:00Z", freq="1h"
            ).tolist()[::-1],
            pd.DataFrame(
                {
                    "time": pd.date_range(
                        "2021-02-28T12:00:00Z", end="2021-03-01T11:59:00Z", freq="1h"
                    ),
                    "other": list(range(48, 36, -1)) + list(range(12, 0, -1)),
                }
            ),
            {
                "start": "2021-02-28T12:00",
                "end": "2021-03-01T12:00",
                "step": "60:00",
                "timezone": "UTC",
            },
            True,
        ),
        (
            # cross DST
            pd.date_range(
                "2020-02-28T12:00:00",
                end="2020-03-20T12:00:00",
                freq="1h",
                tz="America/Denver",
            ),
            pd.DataFrame(
                {
                    "time": pd.date_range(
                        "2021-02-28T12:00:00",
                        end="2021-03-20T11:59:00",
                        freq="1h",
                        tz="America/Denver",
                    ),
                    "other": list(range(12))
                    # feb 29, 2020 data is dropped
                    + list(range(36, 206))
                    # 2021-03-08 02:00, 3/8/2020 02:00 was dst transition
                    + [float("nan")] + list(range(206, 350))
                    # 2021-03-14 was dst transition
                    + list(range(351, 503)),
                }
            ),
            {
                "start": "2021-02-28T12:00",
                "end": "2021-03-20T12:00",
                "step": "60:00",
                "timezone": "America/Denver",
            },
            True,
        ),
    ],
)
def test_reindex_shifting(inp, exp, jti, ats):
    inpdf = pd.DataFrame({"time": inp, "other": list(range(len(inp)))})
    out = utils.reindex_timeseries(inpdf, models.JobTimeindex(**jti), ats)[0]
    pd.testing.assert_frame_equal(out, exp)

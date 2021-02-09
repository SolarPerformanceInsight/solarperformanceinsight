from copy import deepcopy
import datetime as dt
from functools import partial
import re


from hypothesis import given, example, assume
from hypothesis.strategies import floats, booleans, composite, from_regex
import pandas as pd
from pydantic import BaseModel, ValidationError
import pytest


from solarperformanceinsight_api import models


fail_param = partial(
    pytest.param, marks=pytest.mark.xfail(strict=True, raises=ValidationError)
)


class UserStringModel(BaseModel):
    name: str = models.UserString(...)


@pytest.mark.parametrize(
    "inp",
    [
        "a&badString",
        "INSERT INTO;",
        "MoreBad?",
        "waytoolong" * 50,
        "  ",
        ",'",
        " ,'-()",
        "_",
        "0:",
    ],
)
def test_userstring_fail(inp):
    with pytest.raises(ValidationError):
        UserStringModel(name=inp)


def test_userstring_empty():
    assert UserStringModel(name="").name == ""


@given(
    inp=from_regex(
        re.compile(r"[a-z0-9 ,'\(\)_]+", re.IGNORECASE), fullmatch=True
    ).filter(lambda x: re.search(r"[0-9a-z]+", x, re.IGNORECASE) is not None)
)
def test_userstring_success(inp):
    assert UserStringModel(name=inp).name == inp


@given(
    azimuth=floats(min_value=0, max_value=360, exclude_max=True),
    tilt=floats(min_value=0, max_value=90),
)
@example(azimuth=359.999, tilt=90.0)
@example(azimuth=33.9, tilt="2.33")
@example(azimuth=49.823, tilt=179.83)
def test_fixed_tracking(azimuth, tilt):
    out = models.FixedTracking(azimuth=azimuth, tilt=tilt)
    assert out.azimuth == azimuth
    assert out.tilt == float(tilt)


@composite
def outside_az_tilt(draw):
    azimuth = draw(floats())
    tilt = draw(floats())
    assume((azimuth >= 360 or azimuth < 0) or (tilt > 180 or tilt < 0))
    return (azimuth, tilt)


@given(azt=outside_az_tilt())
@example(azt=(360.0, 2.0))
@example(azt=(33.0, "s"))
def test_fixed_tracking_outside(azt):
    azimuth, tilt = azt
    with pytest.raises(ValidationError):
        models.FixedTracking(azimuth=azimuth, tilt=tilt)


@given(
    azimuth=floats(min_value=0, max_value=360, exclude_max=True),
    tilt=floats(min_value=0, max_value=90),
    gcr=floats(min_value=0),
    backtracking=booleans(),
)
@example(azimuth=0.0, tilt=0.0, gcr="0.0", backtracking="no")
def test_singleaxis_tracking(tilt, azimuth, gcr, backtracking):
    out = models.SingleAxisTracking(
        axis_tilt=tilt, axis_azimuth=azimuth, gcr=gcr, backtracking=backtracking
    )
    assert out.axis_tilt == tilt
    assert out.axis_azimuth == azimuth
    assert out.gcr == float(gcr)
    assert out.backtracking == (False if backtracking == "no" else backtracking)


@composite
def outside_az_tilt_gcr(draw):
    azimuth = draw(floats())
    tilt = draw(floats())
    gcr = draw(floats())
    assume((azimuth >= 360 or azimuth < 0) or (tilt > 90 or tilt < 0) or gcr < 0)
    return (azimuth, tilt, gcr)


@given(atg=outside_az_tilt_gcr(), backtracking=booleans())
@example(atg=(9.0, 9.0, 0.0), backtracking="maybe")
@example(atg=(360.0, 0, 0), backtracking=True)
def test_singleaxis_tracking_outside(atg, backtracking):
    azimuth, tilt, gcr = atg
    with pytest.raises(ValidationError):
        models.SingleAxisTracking(
            axis_tilt=tilt, axis_azimuth=azimuth, gcr=gcr, backtracking=backtracking
        )


def test_calculatejob_types():
    # 1A
    assert models.CalculatePerformanceJob(
        calculate="predicted performance"
    )._weather_types == (models.JobDataTypeEnum.original_weather,)
    # 1B
    assert models.CalculatePerformanceJob(
        calculate="expected performance"
    )._weather_types == (models.JobDataTypeEnum.actual_weather,)


def test_comparejob_types():
    # 2A
    cj2A = models.ComparePerformanceJob(
        compare="predicted and actual performance", performance_granularity="inverter"
    )
    assert cj2A._weather_types == (
        models.JobDataTypeEnum.original_weather,
        models.JobDataTypeEnum.actual_weather,
    )
    assert cj2A._performance_types == (models.JobDataTypeEnum.actual_performance,)
    # 2B
    cj2B = models.ComparePerformanceJob(
        compare="predicted and expected performance", performance_granularity="inverter"
    )
    assert cj2B._weather_types == (
        models.JobDataTypeEnum.original_weather,
        models.JobDataTypeEnum.actual_weather,
    )
    assert cj2B._performance_types == (models.JobDataTypeEnum.predicted_performance,)
    # 2C
    cj2C = models.ComparePerformanceJob(
        compare="expected and actual performance", performance_granularity="inverter"
    )
    assert cj2C._weather_types == (models.JobDataTypeEnum.actual_weather,)
    assert cj2C._performance_types == (models.JobDataTypeEnum.actual_performance,)
    # 2D
    cj2D = models.CalculateWeatherAdjustedPRJob(
        calculate="weather-adjusted performance ratio", performance_granularity="system"
    )
    assert cj2D._weather_types == (models.JobDataTypeEnum.actual_weather,)
    assert cj2D._performance_types == (models.JobDataTypeEnum.actual_performance,)


@pytest.mark.parametrize(
    "job_type,weather_granularity,expected",
    [
        (
            dict(calculate="predicted performance"),
            "system",
            [{"schema_path": "/", "type": "original weather data"}],
        ),
        (
            dict(calculate="predicted performance"),
            "inverter",
            [
                {"schema_path": "/inverters/0", "type": "original weather data"},
                {"schema_path": "/inverters/1", "type": "original weather data"},
            ],
        ),
        (
            dict(calculate="predicted performance"),
            "array",
            [
                {
                    "schema_path": "/inverters/0/arrays/0",
                    "type": "original weather data",
                },
                {
                    "schema_path": "/inverters/0/arrays/1",
                    "type": "original weather data",
                },
                {
                    "schema_path": "/inverters/1/arrays/0",
                    "type": "original weather data",
                },
            ],
        ),
        (
            dict(calculate="expected performance"),
            "inverter",
            [
                {"schema_path": "/inverters/0", "type": "actual weather data"},
                {"schema_path": "/inverters/1", "type": "actual weather data"},
            ],
        ),
        (
            dict(
                compare="predicted and actual performance",
                performance_granularity="system",
            ),
            "inverter",
            [
                {"schema_path": "/inverters/0", "type": "original weather data"},
                {"schema_path": "/inverters/1", "type": "original weather data"},
                {"schema_path": "/inverters/0", "type": "actual weather data"},
                {"schema_path": "/inverters/1", "type": "actual weather data"},
                {"schema_path": "/", "type": "actual performance data"},
            ],
        ),
        (
            dict(
                compare="predicted and expected performance",
                performance_granularity="inverter",
            ),
            "inverter",
            [
                {"schema_path": "/inverters/0", "type": "original weather data"},
                {"schema_path": "/inverters/1", "type": "original weather data"},
                {"schema_path": "/inverters/0", "type": "actual weather data"},
                {"schema_path": "/inverters/1", "type": "actual weather data"},
                {"schema_path": "/inverters/0", "type": "predicted performance data"},
                {"schema_path": "/inverters/1", "type": "predicted performance data"},
            ],
        ),
        (
            dict(
                compare="expected and actual performance",
                performance_granularity="system",
            ),
            "array",
            [
                {"schema_path": "/inverters/0/arrays/0", "type": "actual weather data"},
                {"schema_path": "/inverters/0/arrays/1", "type": "actual weather data"},
                {"schema_path": "/inverters/1/arrays/0", "type": "actual weather data"},
                {"schema_path": "/", "type": "actual performance data"},
            ],
        ),
        (
            dict(
                calculate="weather-adjusted performance ratio",
                performance_granularity="inverter",
            ),
            "inverter",
            [
                {"schema_path": "/inverters/0", "type": "actual weather data"},
                {"schema_path": "/inverters/1", "type": "actual weather data"},
                {"schema_path": "/inverters/0", "type": "actual performance data"},
                {"schema_path": "/inverters/1", "type": "actual performance data"},
            ],
        ),
    ],
)
def test_construct_data_items(job_type, weather_granularity, expected):
    param_dict = deepcopy(models.JOB_PARAMS_EXAMPLE)
    param_dict["job_type"] = job_type
    param_dict["weather_granularity"] = weather_granularity
    params = models.JobParameters(**param_dict)
    system_dict = deepcopy(models.SYSTEM_EXAMPLE)
    system_dict["inverters"] = [
        system_dict["inverters"][0],
        system_dict["inverters"][0],
    ]
    system = models.PVSystem(**system_dict)
    arr0 = system.inverters[0].arrays[0]
    system.inverters[0].arrays = [arr0, arr0]

    out = models._construct_data_items(system, params)
    assert out == expected


@pytest.mark.parametrize(
    "start,end,tz",
    (
        ("2020-01-01T07:00:00+07:00", "2021-01-01T06:59:59+07:00", "UTC"),
        ("2020-01-01T00:00:00", "2020-12-31T23:59:59", "UTC"),
        ("2020-01-01T00:00:00", "2021-01-01T00:00:00", "UTC"),
        pytest.param(
            "2020-01-01T00:00:00",
            "2020-12-31T23:59:59",
            None,
            marks=pytest.mark.xfail(strict=True),
        ),
        ("2020-01-01T00:00:00+00:00", "2020-12-31T23:59:59+00:00", None),
    ),
)
def test_jobtimeindex(start, end, tz):
    out = models.JobTimeindex(start=start, end=end, step="15:00", timezone=tz)
    assert out.step == dt.timedelta(minutes=15)
    assert out.timezone == "UTC"
    pd.testing.assert_index_equal(
        out._time_range,
        pd.date_range(
            start="2020-01-01T00:00:00",
            end="2020-12-31T23:59:59",
            freq="15min",
            tz="UTC",
        ),
    )


@pytest.mark.parametrize(
    "start,end,step,tz",
    [
        pytest.param(
            "2020-01-01T00:00:00",
            "2020-02-01T12:39:47",
            "01:00",
            "UTC",
            marks=pytest.mark.xfail(strict=True),
        ),
        ("2020-01-01T00:00:00", "2020-02-01T12:39:47", "01:00", None),
        ("2020-01-01T00:00:00", "2020-02-01T12:39:47", "01:00", "Not a tz"),
        ("2020-01-01T00:00:00", "2020-02-01T12:39:47", "00:00", "UTC"),
        ("2020-01-01T00:00:00", "2020-02-01T12:39:47", "90:00", "UTC"),
        ("2020-01-01T00:00:00+00:00", "2020-02-01T12:39:47", "01:00", "UTC"),
        ("2020-01-01T00:00:00+00:00", "2020-02-01T12:39:47-07:00", "01:00", "UTC"),
        ("2020-01-01T00:00:00", "2019-02-01T12:39:47", "10:00", "UTC"),
        (
            "2020-01-01T00:00:00",
            "2020-02-01T12:39:47",
            -86399999913601.0,  # may cause overflow in dt.timedelta
            "UTC",
        ),
        (
            "2020-01-01T00:00:00",
            "2020-02-01T12:39:47",
            "01:10",
            "UTC",
        ),
    ],
)
def test_jobtimeindex_validation(start, end, step, tz):
    with pytest.raises(ValidationError):
        models.JobTimeindex(start=start, end=end, step=step, timezone=tz)


@pytest.mark.parametrize(
    "irr,temp,expected",
    (
        ("standard", "air", ["time", "ghi", "dni", "dhi", "temp_air", "wind_speed"]),
        (
            "poa",
            "air",
            [
                "time",
                "poa_global",
                "poa_direct",
                "poa_diffuse",
                "temp_air",
                "wind_speed",
            ],
        ),
        (
            "effective",
            "air",
            ["time", "effective_irradiance", "temp_air", "wind_speed"],
        ),
        ("standard", "module", ["time", "ghi", "dni", "dhi", "module_temperature"]),
        (
            "poa",
            "module",
            ["time", "poa_global", "poa_direct", "poa_diffuse", "module_temperature"],
        ),
        ("effective", "module", ["time", "effective_irradiance", "module_temperature"]),
        ("standard", "cell", ["time", "ghi", "dni", "dhi", "cell_temperature"]),
        (
            "poa",
            "cell",
            ["time", "poa_global", "poa_direct", "poa_diffuse", "cell_temperature"],
        ),
        ("effective", "cell", ["time", "effective_irradiance", "cell_temperature"]),
    ),
)
def test_job_parameters_columns(irr, temp, expected, system_def):
    params = deepcopy(models.JOB_PARAMS_EXAMPLE)
    params["irradiance_type"] = irr
    params["temperature_type"] = temp
    mod = models.Job(parameters=params, system_definition=system_def)
    assert mod._weather_columns == expected
    assert mod._performance_columns == ["time", "performance"]


def test_inverter_multiple_arrays(system_def):
    arrd = system_def.inverters[0].arrays[0].dict()
    arr0 = models.PVArray(**{**deepcopy(arrd), "name": "Array 0"})
    arr1 = models.PVArray(**{**deepcopy(arrd), "name": "Array 1"})

    models.Inverter(
        name="inverter",
        make_model="make",
        arrays=[arr0, arr1],
        inverter_parameters=system_def.inverters[0].inverter_parameters,
    )

    arrd["tracking"] = {
        "axis_tilt": 32,
        "axis_azimuth": 180,
        "gcr": 1.2,
        "backtracking": True,
    }
    track0 = models.PVArray(**{**deepcopy(arrd), "name": "Track Array 0"})
    track1 = models.PVArray(**{**deepcopy(arrd), "name": "Track Array 1"})
    with pytest.raises(ValueError):
        models.Inverter(
            name="inverter",
            make_model="make",
            arrays=[track0, track1],
            inverter_parameters=system_def.inverters[0].inverter_parameters,
        )
    # single array ok
    models.Inverter(
        name="inverter",
        make_model="make",
        arrays=[track0],
        inverter_parameters=system_def.inverters[0].inverter_parameters,
    )


def test_pvwatts_module_temp_scaling():
    mod = models.PVWattsModuleParameters(pdc0=100, gamma_pdc=-0.2)
    assert mod.dict() == {"pdc0": 100, "gamma_pdc": -0.2}
    assert mod.pvlib_dict() == {"pdc0": 100, "gamma_pdc": -0.002}


def test_instantiate_array_w_sapm_temperature_parameters(system_def):
    """Regression test for gh #129 """
    sapm_temp_example = {"a": -3.47, "b": -0.0594, "deltaT": 3}

    arrd = deepcopy(system_def.inverters[0].arrays[0].dict())
    arrd["name"] = "PVWatts temperature params"
    arrd["temperature_model_parameters"] = sapm_temp_example
    mod = models.PVArray(**arrd)
    assert mod.temperature_model_parameters.dict() == sapm_temp_example

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


@pytest.fixture()
def timeindex():
    outd = dict(
        start="2020-01-01T00:00:00+00:00",
        end="2020-12-31T23:59:59+00:00",
        step="15:00",
        timezone="UTC",
    )
    return outd, models.JobTimeindex(**outd)


def test_calculate_reference_job(timeindex, system_def, system_id):
    timedict, timeind = timeindex
    job = models.Job(
        system_definition=system_def,
        parameters=dict(
            calculate="reference performance",
            irradiance_type="poa",
            temperature_type="module",
            weather_granularity="array",
            time_parameters=timedict,
            system_id=system_id,
        ),
    )
    assert set(job._data_items.keys()) == {
        ("/inverters/0/arrays/0", models.JobDataTypeEnum.reference_weather),
    }
    assert job._model_chain_method == "run_model_from_poa"
    assert job._data_items[
        ("/inverters/0/arrays/0", "reference weather data")
    ]._data_cols == [
        "time",
        "poa_global",
        "poa_direct",
        "poa_diffuse",
        "module_temperature",
    ]


def test_calculate_modeled_job(timeindex, system_def, system_id):
    timedict, timeind = timeindex
    job = models.Job(
        system_definition=system_def,
        parameters=dict(
            calculate="modeled performance",
            irradiance_type="standard",
            temperature_type="module",
            weather_granularity="inverter",
            time_parameters=timedict,
            system_id=system_id,
        ),
    )
    assert set(job._data_items.keys()) == {
        ("/inverters/0", models.JobDataTypeEnum.actual_weather),
    }
    assert job._model_chain_method == "run_model"
    assert job._data_items[("/inverters/0", "actual weather data")]._data_cols == [
        "time",
        "ghi",
        "dni",
        "dhi",
        "module_temperature",
    ]


def test_compare_modeled_actual_job(timeindex, system_def, system_id):
    # UC 2C
    timedict, timeind = timeindex
    job = models.Job(
        system_definition=system_def,
        parameters=dict(
            compare="modeled and actual performance",
            irradiance_type="effective",
            temperature_type="cell",
            weather_granularity="system",
            performance_granularity="inverter",
            time_parameters=timedict,
            system_id=system_id,
        ),
    )
    assert len(job._data_items) == 2
    assert job._model_chain_method == "run_model_from_effective_irradiance"
    assert job._data_items[("/", "actual weather data")]._data_cols == [
        "time",
        "effective_irradiance",
        "cell_temperature",
    ]
    assert job._data_items[("/inverters/0", "actual performance data")]._data_cols == [
        "time",
        "performance",
    ]


def test_calculate_weather_adjusted_pr_job(timeindex, system_def, system_id):
    # UC 2D
    timedict, timeind = timeindex
    job = models.Job(
        system_definition=system_def,
        parameters=dict(
            calculate="weather-adjusted performance ratio",
            irradiance_type="standard",
            temperature_type="air",
            weather_granularity="inverter",
            performance_granularity="system",
            time_parameters=timedict,
            system_id=system_id,
        ),
    )
    assert len(job._data_items) == 2
    assert job._model_chain_method == "run_model"
    assert job._data_items[("/inverters/0", "actual weather data")]._data_cols == [
        "time",
        "ghi",
        "dni",
        "dhi",
        "temp_air",
        "wind_speed",
    ]
    assert job._data_items[("/", "actual performance data")]._data_cols == [
        "time",
        "performance",
    ]


def test_compare_reference_actual_job_2A1(timeindex, system_def, system_id):
    # UC 2A-1
    timedict, timeind = timeindex
    job = models.Job(
        system_definition=system_def,
        parameters=dict(
            compare="reference and actual performance",
            actual_data_parameters=dict(
                irradiance_type="standard",
                temperature_type="air",
                weather_granularity="system",
                performance_granularity="system",
            ),
            reference_data_parameters=dict(
                data_available="weather, AC, and DC performance",
                irradiance_type="poa",
                temperature_type="module",
                weather_granularity="system",
                performance_granularity="system",
            ),
            time_parameters=timedict,
            system_id=system_id,
        ),
    )
    assert len(job._data_items) == 5
    assert job._model_chain_method is None
    assert job._data_items[("/", "actual weather data")]._data_cols == [
        "time",
        "ghi",
        "dni",
        "dhi",
        "temp_air",
        "wind_speed",
    ]
    assert job._data_items[("/", "reference weather data")]._data_cols == [
        "time",
        "poa_global",
        "poa_direct",
        "poa_diffuse",
        "module_temperature",
    ]
    assert job._data_items[("/", "actual performance data")]._data_cols == [
        "time",
        "performance",
    ]
    assert job._data_items[("/", "reference performance data")]._data_cols == [
        "time",
        "performance",
    ]
    assert job._data_items[("/", "reference DC performance data")]._data_cols == [
        "time",
        "performance",
    ]


def test_compare_reference_actual_job_2A2(timeindex, system_def, system_id):
    # UC 2A-2
    timedict, timeind = timeindex
    job = models.Job(
        system_definition=system_def,
        parameters=dict(
            compare="reference and actual performance",
            actual_data_parameters=dict(
                irradiance_type="poa",
                temperature_type="module",
                weather_granularity="array",
                performance_granularity="inverter",
            ),
            reference_data_parameters=dict(
                data_available="weather and AC performance",
                irradiance_type="standard",
                temperature_type="air",
                weather_granularity="system",
                performance_granularity="system",
            ),
            time_parameters=timedict,
            system_id=system_id,
        ),
    )
    assert len(job._data_items) == 4
    assert job._model_chain_method is None
    assert job._data_items[
        ("/inverters/0/arrays/0", "actual weather data")
    ]._data_cols == [
        "time",
        "poa_global",
        "poa_direct",
        "poa_diffuse",
        "module_temperature",
    ]
    assert job._data_items[("/", "reference weather data")]._data_cols == [
        "time",
        "ghi",
        "dni",
        "dhi",
        "temp_air",
        "wind_speed",
    ]
    assert job._data_items[("/inverters/0", "actual performance data")]._data_cols == [
        "time",
        "performance",
    ]
    assert job._data_items[("/", "reference performance data")]._data_cols == [
        "time",
        "performance",
    ]


def test_compare_reference_actual_job_2A3(system_def, system_id):
    job = models.Job(
        system_definition=system_def,
        parameters=dict(
            compare="monthly reference and actual performance",
            system_id=system_id,
        ),
    )
    assert len(job._data_items) == 4
    assert job._model_chain_method is None
    assert job._data_items[("/", "actual monthly weather data")]._data_cols == [
        "month",
        "total_poa_insolation",
        "average_daytime_cell_temperature",
    ]
    assert job._data_items[("/", "reference monthly weather data")]._data_cols == [
        "month",
        "total_poa_insolation",
        "average_daytime_cell_temperature",
    ]
    assert job._data_items[("/", "actual monthly performance data")]._data_cols == [
        "month",
        "total_energy",
    ]
    assert job._data_items[("/", "reference monthly performance data")]._data_cols == [
        "month",
        "total_energy",
    ]


def test_compare_reference_actual_job_2A4(timeindex, system_def, system_id):
    # UC 2A-4
    timedict, timeind = timeindex
    param_dict = dict(
        compare="reference and actual performance",
        actual_data_parameters=dict(
            irradiance_type="poa",
            temperature_type="module",
            weather_granularity="system",
            performance_granularity="inverter",
        ),
        reference_data_parameters=dict(
            data_available="weather only",
            irradiance_type="standard",
            temperature_type="air",
            weather_granularity="inverter",
        ),
        time_parameters=timedict,
        system_id=system_id,
    )
    job = models.Job(system_definition=system_def, parameters=param_dict)
    assert len(job._data_items) == 3
    assert job._model_chain_method is None
    assert job._data_items[("/", "actual weather data")]._data_cols == [
        "time",
        "poa_global",
        "poa_direct",
        "poa_diffuse",
        "module_temperature",
    ]
    assert job._data_items[("/inverters/0", "reference weather data")]._data_cols == [
        "time",
        "ghi",
        "dni",
        "dhi",
        "temp_air",
        "wind_speed",
    ]
    assert job._data_items[("/inverters/0", "actual performance data")]._data_cols == [
        "time",
        "performance",
    ]

    bad_params = param_dict.copy()
    bad_params["reference_data_parameters"]["performance_granularity"] = "system"
    with pytest.raises(ValidationError):
        models.Job(system_definition=system_def, parameters=bad_params)


def test_compare_reference_modeled_job_2B1(timeindex, system_def, system_id):
    # UC 2B-1
    timedict, timeind = timeindex
    job = models.Job(
        system_definition=system_def,
        parameters=dict(
            compare="reference and modeled performance",
            modeled_data_parameters=dict(
                irradiance_type="standard",
                temperature_type="air",
                weather_granularity="system",
            ),
            reference_data_parameters=dict(
                data_available="weather, AC, and DC performance",
                irradiance_type="poa",
                temperature_type="module",
                weather_granularity="system",
                performance_granularity="system",
            ),
            time_parameters=timedict,
            system_id=system_id,
        ),
    )
    assert len(job._data_items) == 4
    assert job._model_chain_method is None
    assert job._data_items[("/", "actual weather data")]._data_cols == [
        "time",
        "ghi",
        "dni",
        "dhi",
        "temp_air",
        "wind_speed",
    ]
    assert job._data_items[("/", "reference weather data")]._data_cols == [
        "time",
        "poa_global",
        "poa_direct",
        "poa_diffuse",
        "module_temperature",
    ]
    assert job._data_items[("/", "reference performance data")]._data_cols == [
        "time",
        "performance",
    ]
    assert job._data_items[("/", "reference DC performance data")]._data_cols == [
        "time",
        "performance",
    ]


def test_compare_reference_modeled_job_2B2(timeindex, system_def, system_id):
    # UC 2B-2
    timedict, timeind = timeindex
    job = models.Job(
        system_definition=system_def,
        parameters=dict(
            compare="reference and modeled performance",
            modeled_data_parameters=dict(
                irradiance_type="poa",
                temperature_type="module",
                weather_granularity="array",
            ),
            reference_data_parameters=dict(
                data_available="weather and AC performance",
                irradiance_type="standard",
                temperature_type="air",
                weather_granularity="system",
                performance_granularity="system",
            ),
            time_parameters=timedict,
            system_id=system_id,
        ),
    )
    assert len(job._data_items) == 3
    assert job._model_chain_method is None
    assert job._data_items[
        ("/inverters/0/arrays/0", "actual weather data")
    ]._data_cols == [
        "time",
        "poa_global",
        "poa_direct",
        "poa_diffuse",
        "module_temperature",
    ]
    assert job._data_items[("/", "reference weather data")]._data_cols == [
        "time",
        "ghi",
        "dni",
        "dhi",
        "temp_air",
        "wind_speed",
    ]
    assert job._data_items[("/", "reference performance data")]._data_cols == [
        "time",
        "performance",
    ]


def test_compare_reference_modeled_job_2B3(timeindex, system_def, system_id):
    # UC 2B-3
    timedict, timeind = timeindex
    param_dict = dict(
        compare="reference and modeled performance",
        modeled_data_parameters=dict(
            irradiance_type="poa",
            temperature_type="module",
            weather_granularity="system",
        ),
        reference_data_parameters=dict(
            data_available="weather only",
            irradiance_type="standard",
            temperature_type="air",
            weather_granularity="inverter",
        ),
        time_parameters=timedict,
        system_id=system_id,
    )
    job = models.Job(system_definition=system_def, parameters=param_dict)
    assert len(job._data_items) == 2
    assert job._model_chain_method is None
    assert job._data_items[("/", "actual weather data")]._data_cols == [
        "time",
        "poa_global",
        "poa_direct",
        "poa_diffuse",
        "module_temperature",
    ]
    assert job._data_items[("/inverters/0", "reference weather data")]._data_cols == [
        "time",
        "ghi",
        "dni",
        "dhi",
        "temp_air",
        "wind_speed",
    ]
    bad_params = param_dict.copy()
    bad_params["reference_data_parameters"]["performance_granularity"] = "system"
    with pytest.raises(ValidationError):
        models.Job(system_definition=system_def, parameters=bad_params)


@pytest.mark.parametrize(
    "start,end,tz,exp",
    (
        (
            "2020-01-01T07:00:00+07:00",
            "2021-01-01T06:59:59+07:00",
            "UTC",
            pd.date_range(
                start="2020-01-01T00:00:00",
                end="2020-12-31T23:59:59",
                freq="15min",
                tz="UTC",
            ),
        ),
        (
            "2020-01-01T00:00:00",
            "2020-12-31T23:59:59",
            "UTC",
            pd.date_range(
                start="2020-01-01T00:00:00",
                end="2020-12-31T23:59:59",
                freq="15min",
                tz="UTC",
            ),
        ),
        (
            "2020-01-01T00:00:00",
            "2021-01-01T00:00:00",
            "UTC",
            pd.date_range(
                start="2020-01-01T00:00:00",
                end="2020-12-31T23:59:59",
                freq="15min",
                tz="UTC",
            ),
        ),
        pytest.param(
            "2020-01-01T00:00:00",
            "2020-12-31T23:59:59",
            None,
            None,
            marks=pytest.mark.xfail(strict=True),
        ),
        (
            "2020-01-01T00:00:00+00:00",
            "2020-12-31T23:59:59+00:00",
            None,
            pd.date_range(
                start="2020-01-01T00:00:00",
                end="2020-12-31T23:59:59",
                freq="15min",
                tz="UTC",
            ),
        ),
        (
            "2020-01-01T00:00:00",
            "2020-12-31T23:59:59",
            "America/Denver",
            pd.DatetimeIndex(
                list(
                    pd.date_range(
                        start="2020-01-01T00:00:00",
                        end="2020-11-01T01:59:59",
                        ambiguous=True,
                        freq="15min",
                        tz="America/Denver",
                    ).union(  # dst transition times from march dropped
                        # dst transition back 11/1 01:00 is in -06:00 tz
                        pd.date_range(
                            start="2020-11-01T02:00:00-07:00",
                            end="2020-12-31T23:59:59-07:00",
                            freq="15min",
                        ).tz_convert("America/Denver")
                    )
                )
            ),
        ),
    ),
)
def test_jobtimeindex(start, end, tz, exp):
    out = models.JobTimeindex(start=start, end=end, step="15:00", timezone=tz)
    assert out.step == dt.timedelta(minutes=15)
    assert out.timezone == tz or "UTC"
    pd.testing.assert_index_equal(out._time_range, exp)


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
        (None, "2020-01-09T23:33Z", "05:00", None),
        ("2020-01-09T23:33Z", None, "05:00", None),
    ],
)
def test_jobtimeindex_validation(start, end, step, tz):
    with pytest.raises(ValidationError):
        models.JobTimeindex(start=start, end=end, step=step, timezone=tz)


@pytest.mark.parametrize("type_", ("reference weather data", "actual weather data"))
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
def test_jobdataitem_columns(irr, temp, expected, type_):
    jdi = models.JobDataItem.from_types(
        "/", type_, irradiance_type=irr, temperature_type=temp
    )
    assert jdi._data_cols == expected


def test_jobdataitem_columns_others():
    for type_ in (
        "reference performance data",
        "reference DC performance data",
        "modeled performance data",
        "actual performance data",
    ):
        models.JobDataItem.from_types("/", type_)._data_cols == ["time", "performance"]
    for type_ in ("actual monthly weather data", "reference monthly weather data"):
        models.JobDataItem.from_types("/", type_)._data_cols == [
            "time",
            "total_poa_insolation",
            "average_daytime_cell_temperature",
        ]
    for type_ in (
        "actual monthly performance data",
        "reference monthly performance data",
    ):
        models.JobDataItem.from_types("/", type_)._data_cols == ["time", "total_energy"]


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


def test_pvsystem_extra_param(system_def):
    with pytest.raises(ValidationError):
        models.PVSystem(**system_def.dict(), extra_field="not_valid")


def test_cec_module_no_gamma():
    cec = models.CECModuleParameters(
        alpha_sc=0.004423,
        a_ref=0.976,
        I_L_ref=4.98,
        I_o_ref=8.8e-10,
        R_sh_ref=148.82,
        R_s=0.32,
        gamma_r=-0.487,
        cells_in_series=36,
        Adjust=10.48,
    )
    assert "gamma_r" in cec.dict()
    assert "gamma_r" not in cec.pvlib_dict()


def test_array_gamma(system_def):
    cec = dict(
        alpha_sc=0.004423,
        a_ref=0.976,
        I_L_ref=4.98,
        I_o_ref=8.8e-10,
        R_sh_ref=148.82,
        R_s=0.32,
        gamma_r=-0.487,
        cells_in_series=36,
        Adjust=10.48,
    )
    arrd = deepcopy(system_def.inverters[0].arrays[0].dict())
    mod = models.PVArray(**arrd)
    assert mod.module_parameters._gamma is None  # PVsyst

    arrd["module_parameters"] = cec
    mod = models.PVArray(**arrd)
    assert mod.module_parameters._gamma == -4.87e-3

    arrd["module_parameters"] = {"pdc0": 100, "gamma_pdc": -0.328}
    mod = models.PVArray(**arrd)
    assert mod.module_parameters._gamma == -3.28e-3

from functools import partial
from pydantic import BaseModel, ValidationError
import pytest


from solarperformanceinsight_api import models


fail_param = partial(
    pytest.param, marks=pytest.mark.xfail(strict=True, raises=ValidationError)
)


@pytest.mark.parametrize(
    "inp,exp",
    [
        ("axis_tilt", "axisTilt"),
        ("tilt", "tilt"),
        ("longer_string_name", "longerStringName"),
    ],
)
def test_to_camel(inp, exp):
    assert exp == models.to_camel(inp)


class UserString(BaseModel):
    name: models.userstring


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
    ],
)
def test_userstring_fail(inp):
    with pytest.raises(ValidationError):
        UserString(name=inp)


@pytest.mark.parametrize(
    "inp",
    ["A long but OK name", "A comma, is here", "a (mostly) ok - 99891", " ,'-() word_"],
)
def test_userstring_success(inp):
    assert UserString(name=inp).name == inp


@pytest.mark.parametrize(
    "azimuth", [100, 0, 359.999, fail_param(360), fail_param(-138.00), fail_param("s")]
)
@pytest.mark.parametrize(
    "tilt", [100, 0, 180, 99.83, fail_param(-19), fail_param("asd")]
)
def test_fixed_tracking(azimuth, tilt):
    out = models.FixedTracking(azimuth=azimuth, tilt=tilt)
    assert out.azimuth == azimuth
    assert out.tilt == tilt


@pytest.mark.parametrize("azimuth", [0, 38.93, fail_param(360.0), fail_param("str")])
@pytest.mark.parametrize(
    "tilt", [0, 66, fail_param(99.9), fail_param(-1e-3), fail_param("fail")]
)
@pytest.mark.parametrize("gcr", [0, 3.023, "3.29", fail_param(-1.8)])
@pytest.mark.parametrize("backtracking", [True, False, fail_param("s")])
def test_singleaxis_tracking(tilt, azimuth, gcr, backtracking):
    out = models.SingleAxisTracking(
        axisTilt=tilt, axisAzimuth=azimuth, gcr=gcr, backtracking=backtracking
    )
    assert out.axis_tilt == tilt
    assert out.axis_azimuth == azimuth
    assert out.gcr == float(gcr)
    assert out.backtracking == backtracking

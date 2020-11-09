from functools import partial
import re


from hypothesis import given, example, assume
from hypothesis.strategies import floats, booleans, composite, from_regex
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
        "0:",
    ],
)
def test_userstring_fail(inp):
    with pytest.raises(ValidationError):
        UserString(name=inp)


@given(
    inp=from_regex(
        re.compile(r"[a-z0-9 ,'\(\)_]+", re.IGNORECASE), fullmatch=True
    ).filter(lambda x: re.search(r"[0-9a-z]+", x, re.IGNORECASE) is not None)
)
def test_userstring_success(inp):
    assert UserString(name=inp).name == inp


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
    tilt=floats(min_value=0, max_value=180),
    gcr=floats(min_value=0),
    backtracking=booleans(),
)
@example(azimuth=0.0, tilt=0.0, gcr="0.0", backtracking="no")
def test_singleaxis_tracking(tilt, azimuth, gcr, backtracking):
    out = models.SingleAxisTracking(
        axisTilt=tilt, axisAzimuth=azimuth, gcr=gcr, backtracking=backtracking
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
    assume((azimuth >= 360 or azimuth < 0) or (tilt > 180 or tilt < 0) or gcr < 0)
    return (azimuth, tilt, gcr)


@given(atg=outside_az_tilt_gcr(), backtracking=booleans())
@example(atg=(9.0, 9.0, 0.0), backtracking="maybe")
@example(atg=(360.0, 0, 0), backtracking=True)
def test_singleaxis_tracking_outside(atg, backtracking):
    azimuth, tilt, gcr = atg
    with pytest.raises(ValidationError):
        models.SingleAxisTracking(
            axisTilt=tilt, axisAzimuth=azimuth, gcr=gcr, backtracking=backtracking
        )

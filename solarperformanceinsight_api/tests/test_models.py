from pydantic import BaseModel, ValidationError
import pytest


from solarperformanceinsight_api import models


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


def test_failure():
    raise TypeError()

from typing import Union, List
from pydantic import BaseModel, condecimal, constr


# allows word chars, space, comma, apostrophe, hyphen, parentheses, and underscore
userstring = constr(regex=r"^(?!\W+$)(?![_ ',\-\(\)]+$)[\w ',\-\(\)]+$", max_length=128)


class FixedTracking(BaseModel):
    """Shows up in openapi stuff"""

    tilt: condecimal(ge=0, le=180)
    azimuth: condecimal(ge=0, le=360)


class SingleAxisTracking(BaseModel):
    axisTilt: condecimal(ge=0, le=90)
    axisAzimuth: condecimal(ge=0, le=360)
    gcr: condecimal(ge=0)


class PVArray(BaseModel):
    name: userstring
    tracking: Union[FixedTracking, SingleAxisTracking]


class Inverter(BaseModel):
    name: userstring
    arrays: List[PVArray]


class PVSystem(BaseModel):
    name: userstring
    latitude: condecimal(ge=-90, le=90)
    longitude: condecimal(ge=-180, le=180)
    elevation: condecimal(ge=-300)
    albedo: condecimal(ge=0)
    inverters: List[Inverter]


class NameSystem(BaseModel):
    name: userstring

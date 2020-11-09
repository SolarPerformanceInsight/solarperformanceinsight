from typing import Union, List, Optional
from pydantic import BaseModel, confloat, constr, Field


# allows word chars, space, comma, apostrophe, hyphen, parentheses, and underscore
userstring = constr(regex=r"^(?!\W+$)(?![_ ',\-\(\)]+$)[\w ',\-\(\)]+$", max_length=128)

optuserstring = Optional[userstring]


class FixedTracking(BaseModel):
    """Parameters for a fixed tilt array"""

    tilt: confloat(ge=0, le=180) = Field(
        ..., description="Tilt of modules in degrees from horizontal"
    )
    azimuth: confloat(ge=0, lt=360.0) = Field(
        ..., description="Azimuth of modules relative to North in degrees"
    )


class SingleAxisTracking(BaseModel):
    """Parameters for a single axis tracking array"""

    axis_tilt: confloat(ge=0, le=90) = Field(
        ...,
        title="Axis Tilt",
        description="Tilt of single axis tracker in degrees from horizontal",
    )
    axis_azimuth: confloat(ge=0, lt=360.0) = Field(
        ...,
        title="Axis Azimiuth",
        description="Azimuth of tracker axis from North in degrees",
    )
    gcr: confloat(ge=0) = Field(..., title="GCR", description="Ground coverage ratio")
    backtracking: bool = Field(
        ..., description="If the tracking system supports backtracking"
    )


class ModuleParameters(BaseModel):
    """Parameters for the modules that make up an array"""

    pass


class TemperatureParameters(BaseModel):
    """Parameters for the temperature model of the modules"""

    pass


class PVArray(BaseModel):
    """Parameters of a PV array that feeds into one inverter"""

    name: optuserstring = Field(None, description="Name of this array")
    make_model: optuserstring = Field(
        None,
        title="Make & Model",
        description="Make and model of the PV modules in this array",
    )
    module_parameters: ModuleParameters = Field(
        ...,
        title="Module Parameters",
        description="Parameters describing PV modules in this array",
    )
    temperature_model_parameters: TemperatureParameters = Field(
        ...,
        title="Temperature Model Parameters",
        description=(
            "Parameters describing the temperature characteristics of the modules"
        ),
    )
    tracking: Union[FixedTracking, SingleAxisTracking] = Field(
        ..., description="Parameters describing single-axis tracking or fixed mounting"
    )
    modules_per_string: Union[int, None] = Field(
        ..., title="Modules Per String", description="Number of PV modules per string"
    )
    strings: Union[int, None] = Field(..., description="Number of Strings")


class Losses(BaseModel):
    """Parameters describing losses in the arrays and power conversion"""

    pass


class InverterParameters(BaseModel):
    """Power conversion parameters of an inverter"""

    pass


class Inverter(BaseModel):
    """Parameters for a single inverter feeding into a PV system"""

    name: optuserstring = Field(None, description="Name of this inverter")
    make_model: optuserstring = Field(
        None, title="Make & Model", description="Make and model of the inverter"
    )
    arrays: List[PVArray] = Field(
        ..., description="PV arrays that are connected to this inverter"
    )
    losses: Losses = Field(..., description="Parameters describing the array losses")
    inverter_parameters: InverterParameters = Field(
        ...,
        title="Inverter Parameters",
        description="Power conversion parameters for the inverter",
    )


class PVSystem(BaseModel):
    """Parameters for an entire PV system at some location"""

    name: userstring = Field(..., description="Name of the system")
    latitude: confloat(ge=-90, le=90) = Field(
        ..., description="Latitude of the system in degrees North"
    )
    longitude: confloat(ge=-180, le=180) = Field(
        ..., description="Longitude of the system in degrees East"
    )
    elevation: confloat(ge=-300) = Field(
        ..., description="Elevation of the system in meters"
    )
    albedo: confloat(ge=0) = Field(
        ..., description="Albedo of the surface around the system"
    )
    inverters: List[Inverter] = Field(
        ..., description="Inverters that are connected to make up this system"
    )

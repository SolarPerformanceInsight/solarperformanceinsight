import datetime as dt
from typing import Union, List, Optional, Any
from pydantic import BaseModel, Field
from pydantic.fields import Undefined
from pydantic.types import UUID


# allows word chars, space, comma, apostrophe, hyphen, parentheses, underscore
# and empty string
def UserString(default: Any = Undefined, *, title: str = None, description: str = None):
    return Field(
        default,
        title=title,
        description=description,
        max_length=128,
        regex=r"^(?!\W+$)(?![_ ',\-\(\)]+$)[\w ',\-\(\)]*$",
    )


class FixedTracking(BaseModel):
    """Parameters for a fixed tilt array"""

    tilt: float = Field(
        ..., description="Tilt of modules in degrees from horizontal", ge=0, le=180
    )
    azimuth: float = Field(
        ...,
        description="Azimuth of modules relative to North in degrees",
        ge=0,
        lt=360.0,
    )


class SingleAxisTracking(BaseModel):
    """Parameters for a single axis tracking array"""

    axis_tilt: float = Field(
        ...,
        title="Axis Tilt",
        description="Tilt of single axis tracker in degrees from horizontal",
        ge=0,
        le=90,
    )
    axis_azimuth: float = Field(
        ...,
        title="Axis Azimiuth",
        description="Azimuth of tracker axis from North in degrees",
        ge=0,
        lt=360.0,
    )
    gcr: float = Field(..., title="GCR", description="Ground coverage ratio", ge=0)
    backtracking: bool = Field(
        ..., description="If the tracking system supports backtracking"
    )


class PVsystModuleParameters(BaseModel):
    """Parameters for the modules that make up an array in a PVsyst-like model"""

    alpha_sc: float = Field(
        ...,
        description=(
            "Short-circuit current temperature coefficient of the module "
            "in units of A/C"
        ),
    )
    gamma_ref: float = Field(..., description="Diode ideality factor", ge=0)
    mu_gamma: float = Field(
        ...,
        description="Temperature coefficient for the diode ideality factor, 1/K",
    )
    I_L_ref: float = Field(
        ...,
        description=(
            "Light-generated current (or photocurrent) at reference conditions,"
            "in amperes"
        ),
    )
    I_o_ref: float = Field(
        ...,
        description=(
            "Dark or diode reverse saturation current at reference conditions,"
            "in amperes"
        ),
    )
    R_sh_ref: float = Field(
        ...,
        description="Shunt resistance at reference conditions, in ohms",
    )
    R_sh_0: float = Field(
        ..., description="Shunt resistance at zero irradiance conditions, in ohms"
    )
    R_s: float = Field(
        ..., description="Series resistance at reference conditions, in ohms"
    )
    cells_in_series: int = Field(
        ..., description="Number of cells connected in series", ge=0
    )
    R_sh_exp: float = Field(
        5.5, description="Exponent in the equation for shunt resistance, unitless"
    )
    EgRef: float = Field(
        1.121,
        description=(
            "Energy bandgap at reference temperatures in units of eV. "
            "1.121 eV for crystsalline silicon."
        ),
        gt=0,
    )


class PVWattsModuleParameters(BaseModel):
    """Parameters for the modules that make up an array in a PVWatts-like model"""

    pdc0: float = Field(
        ...,
        description="Power of the modules at 1000 W/m^2 and cell reference temperature",
    )
    gamma_pdc: float = Field(
        ...,
        description=(
            "Temperature coefficient in units of 1/C. "
            "Typically -0.002 to -0.005 per degree C"
        ),
    )


class PVsystTemperatureParameters(BaseModel):
    """Parameters for the cell temperature model of the modules in a
    PVSyst-like model"""

    u_c: float = Field(
        29.0, description="Combined heat loss factor coefficient, units of W/m^2/C"
    )
    u_v: float = Field(
        0.0,
        description=(
            "Combined heat loss factor influenced by wind, units of (W/m^2)/(C m/s)"
        ),
    )
    eta_m: float = Field(0.1, description="Module external efficiency as a fraction")
    alpha_absorption: float = Field(0.9, description="Absorption coefficient")


class SAPMTemperatureParameters(BaseModel):
    """Parameters for the cell temperature model of the modules in the
    Sandia Array Performance Model"""

    a: float = Field(
        ..., description="Parameter a of the Sandia Array Performance Model"
    )
    b: float = Field(
        ..., description="Parameter b of the Sandia Array Performance Model"
    )
    deltaT: float = Field(
        ..., description="Parameter delta T of the Sandia Array Performance Model"
    )


class PVArray(BaseModel):
    """Parameters of a PV array that feeds into one inverter"""

    name: str = UserString("", description="Name of this array")
    make_model: str = UserString(
        "",
        title="Make & Model",
        description="Make and model of the PV modules in this array",
    )
    module_parameters: Union[PVsystModuleParameters, PVWattsModuleParameters] = Field(
        ...,
        title="Module Parameters",
        description="Parameters describing PV modules in this array",
    )
    temperature_model_parameters: Union[
        PVsystTemperatureParameters, SAPMTemperatureParameters
    ] = Field(
        ...,
        title="Temperature Model Parameters",
        description=(
            "Parameters describing the temperature characteristics of the modules"
        ),
    )
    tracking: Union[FixedTracking, SingleAxisTracking] = Field(
        ..., description="Parameters describing single-axis tracking or fixed mounting"
    )
    modules_per_string: int = Field(
        ...,
        title="Modules Per String",
        description="Number of PV modules per string",
        gt=0,
    )
    strings: int = Field(..., description="Number of Strings", gt=0)


class PVWattsLosses(BaseModel):
    """Parameters describing the PVWatts system loss model"""

    soiling: float = Field(2.0, description="Soiling loss, %")
    shading: float = Field(3.0, description="Shading loss, %")
    snow: float = Field(0.0, description="Snow loss, %")
    mismatch: float = Field(2.0, description="Mismatch loss, %")
    wiring: float = Field(2.0, description="Wiring loss, %")
    connections: float = Field(0.5, description="Connections loss, %")
    lid: float = Field(1.5, description="Light induced degradation, %")
    nameplate_rating: float = Field(1.0, description="Nameplate Rating loss, %")
    age: float = Field(0.0, description="Age loss, %")
    availability: float = Field(3.0, description="Availability loss, %")


class PVWattsInverterParameters(BaseModel):
    """DC-AC power conversion parameters of an inverter for the PVWatts model"""

    pdc0: float = Field(..., description="DC input limit of the inverter")
    eta_inv_nom: float = Field(
        0.96, description="Nominal inverter efficiency, unitless"
    )
    eta_inv_ref: float = Field(
        0.9637, description="Reference inverter efficiency, unitless"
    )


class SandiaInverterParameters(BaseModel):
    """DC-AC power conversion parameters of an inverter for Sandia's
    Grid-Connected PV Inverter model"""

    Paco: float = Field(..., description="AC power rating of the inverter, W")
    Pdco: float = Field(
        ...,
        description=(
            "DC power rating of the inverter, typically assumed to be equal to the "
            "PV array maximum power, W"
        ),
    )
    Vdco: float = Field(
        ...,
        description=(
            "DC voltage at which the AC power rating is achieved at reference "
            "operating conditions, V"
        ),
    )
    Pso: float = Field(
        ...,
        description=(
            "DC power required to start the inversion process or self consumption "
            "by the inverter, W"
        ),
    )
    C0: float = Field(
        ...,
        description=(
            "Parameter defining the curvature of the relationship between AC "
            "power and DC power at reference operating conditions, 1/W"
        ),
    )
    C1: float = Field(
        ...,
        description=(
            "Empirical coefficient allowing Pdco to vary linearly with DC "
            "voltage input, 1/V"
        ),
    )
    C2: float = Field(
        ...,
        description=(
            "Empirical coefficient allowing Pso to vary linearly with DC "
            "voltage input, 1/V"
        ),
    )
    C3: float = Field(
        ...,
        description=(
            "Empirical coefficient allowing C0 to vary linearly with DC "
            "voltage input, 1/V"
        ),
    )
    Pnt: float = Field(
        ..., description="AC power consumed by the inverter at night (night tare), W"
    )


class Inverter(BaseModel):
    """Parameters for a single inverter feeding into a PV system"""

    name: str = UserString("", description="Name of this inverter")
    make_model: str = UserString(
        "",
        title="Make & Model",
        description="Make and model of the inverter",
    )
    arrays: List[PVArray] = Field(
        ..., description="PV arrays that are connected to this inverter"
    )
    losses: Optional[PVWattsLosses] = Field(
        {}, description="Parameters describing the array losses"
    )
    inverter_parameters: Union[
        PVWattsInverterParameters, SandiaInverterParameters
    ] = Field(
        ...,
        title="Inverter Parameters",
        description="Power conversion parameters for the inverter",
    )


class PVSystem(BaseModel):
    """Parameters for an entire PV system at some location"""

    name: str = UserString(
        ...,
        description="Name of the system",
    )
    latitude: float = Field(
        ..., description="Latitude of the system in degrees North", ge=-90, le=90
    )
    longitude: float = Field(
        ..., description="Longitude of the system in degrees East", ge=-180, le=180
    )
    elevation: float = Field(
        ..., description="Elevation of the system in meters", ge=-300
    )
    albedo: float = Field(
        ..., description="Albedo of the surface around the system", ge=0
    )
    inverters: List[Inverter] = Field(
        ..., description="Inverters that are connected to make up this system"
    )


class CreatedPVSystemID(BaseModel):
    system_id: UUID = Field(..., description="Unique identifier of the system")


class StoredPVSystem(CreatedPVSystemID):
    created_at: dt.datetime = Field(..., description="Datetime system was created")
    modified_at: dt.datetime = Field(..., description="Datetime system last modified")
    definition: PVSystem

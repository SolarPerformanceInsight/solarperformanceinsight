from typing import Union, List, Optional
from pydantic import BaseModel, confloat, constr, Field, conint
from pydantic.types import UUID


# allows word chars, space, comma, apostrophe, hyphen, parentheses, underscore
# and empty string
userstring = constr(regex=r"^(?!\W+$)(?![_ ',\-\(\)]+$)[\w ',\-\(\)]*$", max_length=128)


class FixedTracking(BaseModel):
    """Parameters for a fixed tilt array"""

    tilt: confloat(ge=0, le=180) = Field(
        ..., description="Tilt of modules in degrees from horizontal"
    )
    azimuth: confloat(ge=0, lt=360.0) = Field(
        ..., description="Azimuth of modules clockwise from North in degrees"
    )


class SingleAxisTracking(BaseModel):
    """Parameters for a single axis tracking array"""

    axis_tilt: confloat(ge=0, le=90) = Field(
        ...,
        title="Axis Tilt",
        description="Tilt of tracker axis in degrees from horizontal",
    )
    axis_azimuth: confloat(ge=0, lt=360.0) = Field(
        ...,
        title="Axis Azimiuth",
        description="Azimuth of tracker axis clockwise from North in degrees",
    )
    gcr: confloat(ge=0) = Field(
        ..., title="GCR",
        description=(
            "Ground coverage ratio: ratio of module length to the spacing"
            " between trackers"),
        )
    backtracking: bool = Field(
        ..., description="True if the tracking system supports backtracking"
    )


class PVsystModuleParameters(BaseModel):
    """Parameters for the modules that make up an array in a PVsyst-like model"""

    alpha_sc: confloat() = Field(
        ...,
        description=(
            "Short-circuit current temperature coefficient of the module "
            "in units of A/C"
        ),
    )
    gamma_ref: confloat(ge=0) = Field(..., description="Diode ideality factor")
    mu_gamma: confloat() = Field(
        ...,
        description="Temperature coefficient for the diode ideality factor, 1/K",
    )
    I_L_ref: confloat() = Field(
        ...,
        description=(
            "Light-generated current (or photocurrent) at reference conditions,"
            "in amperes"
        ),
    )
    I_o_ref: confloat() = Field(
        ...,
        description=(
            "Dark or diode reverse saturation current at reference conditions,"
            "in amperes"
        ),
    )
    R_sh_ref: confloat() = Field(
        ...,
        description="Shunt resistance at reference conditions, in ohms",
    )
    R_sh_0: confloat() = Field(
        ..., description="Shunt resistance at zero irradiance conditions, in ohms"
    )
    R_s: confloat() = Field(
        ..., description="Series resistance at reference conditions, in ohms"
    )
    cells_in_series: conint(ge=0) = Field(
        ..., description="Number of cells connected in series in a module"
    )
    R_sh_exp: confloat() = Field(
        5.5, description="Exponent in the equation for shunt resistance, unitless"
    )
    EgRef: confloat(gt=0) = Field(
        1.121,
        description=(
            "Energy bandgap at reference temperature in units of eV. "
            "1.121 eV for crystsalline silicon."
        ),
    )


class PVWattsModuleParameters(BaseModel):
    """Parameters for the modules that make up an array in a PVWatts-like model"""

    pdc0: confloat() = Field(
        ...,
        description="Power of the modules at 1000 W/m^2 and cell reference temperature",
    )
    gamma_pdc: confloat() = Field(
        ...,
        description=(
            "Temperature coefficient of power in units of 1/C. "
            "Typically -0.002 to -0.005 per degree C"
        ),
    )


class PVsystTemperatureParameters(BaseModel):
    """Parameters for the cell temperature model of the modules in a
    PVSyst-like model"""

    u_c: confloat() = Field(
        29.0, description="Combined heat loss factor coefficient, units of W/m^2/C"
    )
    u_v: confloat() = Field(
        0.0,
        description=(
            "Combined heat loss factor influenced by wind, units of (W/m^2)/(C m/s)"
        ),
    )
    eta_m: confloat() = Field(
        0.1, description="Module external efficiency as a fraction"
    )
    alpha_absorption: confloat() = Field(0.9, description="Absorption coefficient")


class SAPMTemperatureParameters(BaseModel):
    """Parameters for the cell temperature model of the modules in the
    Sandia Array Performance Model"""

    a: confloat() = Field(
        ..., description="Parameter a of the Sandia Array Performance Model"
    )
    b: confloat() = Field(
        ..., description="Parameter b of the Sandia Array Performance Model"
    )
    deltaT: confloat() = Field(
        ..., description="Parameter delta T of the Sandia Array Performance Model"
    )


class PVArray(BaseModel):
    """Parameters of a PV array that feeds into one inverter"""

    name: userstring = Field("", description="Name of this array")
    make_model: userstring = Field(
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
    modules_per_string: conint(gt=0) = Field(
        ..., title="Modules Per String", description="Number of PV modules per string"
    )
    strings: conint(gt=0) = Field(..., description="Number of parallel strings in the array")


class PVWattsLosses(BaseModel):
    """Parameters describing the PVWatts system loss model"""

    soiling: confloat() = Field(2.0, description="Soiling loss, %")
    shading: confloat() = Field(3.0, description="Shading loss, %")
    snow: confloat() = Field(0.0, description="Snow loss, %")
    mismatch: confloat() = Field(2.0, description="Mismatch loss, %")
    wiring: confloat() = Field(2.0, description="Wiring loss, %")
    connections: confloat() = Field(0.5, description="Connections loss, %")
    lid: confloat() = Field(1.5, description="Light induced degradation, %")
    nameplate_rating: confloat() = Field(1.0, description="Nameplate Rating loss, %")
    age: confloat() = Field(0.0, description="Age loss, %")
    availability: confloat() = Field(3.0, description="Availability loss, %")


class PVWattsInverterParameters(BaseModel):
    """DC-AC power conversion parameters of an inverter for the PVWatts model"""

    pdc0: confloat() = Field(
        ...,
        description=(
            "DC power input which produces the rated AC output power at the "
            "nominal DC voltage of the inverter")
        )
    eta_inv_nom: confloat() = Field(
        0.96, description="Nominal inverter efficiency, unitless"
    )
    eta_inv_ref: confloat() = Field(
        0.9637, description="Reference inverter efficiency, unitless"
    )


class SandiaInverterParameters(BaseModel):
    """DC-AC power conversion parameters of an inverter for Sandia's
    Grid-Connected PV Inverter model"""

    Paco: confloat() = Field(..., description="AC power rating of the inverter, W")
    Pdco: confloat() = Field(
        ...,
        description=(
            "DC power which produces the rated AC output power at the "
            "nominal DC voltage of the inverter, W"
        ),
    )
    Vdco: confloat() = Field(
        ...,
        description=(
            "Nominal DC voltage at which the AC power rating is determined, V"
        ),
    )
    Pso: confloat() = Field(
        ...,
        description=(
            "DC power required to start the inversion process, assumed equal "
            "to self consumption by the inverter, W"
        ),
    )
    C0: confloat() = Field(
        ...,
        description=(
            "Parameter defining the curvature of the relationship between AC "
            "power and DC power at reference operating conditions, 1/W"
        ),
    )
    C1: confloat() = Field(
        ...,
        description=(
            "Empirical coefficient allowing Pdco to vary linearly with DC "
            "voltage input, 1/V"
        ),
    )
    C2: confloat() = Field(
        ...,
        description=(
            "Empirical coefficient allowing Pso to vary linearly with DC "
            "voltage input, 1/V"
        ),
    )
    C3: confloat() = Field(
        ...,
        description=(
            "Empirical coefficient allowing C0 to vary linearly with DC "
            "voltage input, 1/V"
        ),
    )
    Pnt: confloat() = Field(
        ..., description=(
            "AC power consumed by the inverter when no AC power is exported "
            " (i.e., night tare), W"
            ),
    )


class Inverter(BaseModel):
    """Parameters for a single inverter feeding into a PV system"""

    name: userstring = Field("", description="Name of this inverter")
    make_model: userstring = Field(
        "", title="Make & Model", description="Make and model of the inverter"
    )
    arrays: List[PVArray] = Field(
        ..., description="Names of the PV arrays that are connected to this inverter"
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

    name: userstring = Field(..., description="Name of the system")
    latitude: confloat(ge=-90, le=90) = Field(
        ..., description="Latitude of the system in degrees North"
    )
    longitude: confloat(ge=-180, le=180) = Field(
        ..., description="Longitude of the system in degrees East"
    )
    elevation: confloat(ge=-300) = Field(
        ..., description="Elevation of the system above sea level in meters"
    )
    albedo: confloat(ge=0) = Field(
        ..., description="Albedo of the surface around the system"
    )
    inverters: List[Inverter] = Field(
        ..., description="Names of the inverters that are connected to make up this system"
    )


class StoredPVSystem(PVSystem):
    system_id: UUID = Field(..., description="Unique identifier of the system")

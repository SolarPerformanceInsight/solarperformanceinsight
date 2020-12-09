"""Module to translate models.py into pvlib objects and to run the
pvlib models.
"""
from typing import Union, Tuple, Any, Dict, List


from pvlib.location import Location  # type: ignore
from pvlib.modelchain import ModelChain  # type: ignore
from pvlib.pvsystem import PVSystem  # type: ignore
from pvlib.tracking import SingleAxisTracker  # type: ignore

from . import models


def construct_location(system: models.PVSystem) -> Location:
    """Construct a pvlib Location object from a PVSystem"""
    return Location(
        latitude=system.latitude,
        longitude=system.longitude,
        altitude=system.elevation,
        name=system.name,
    )


def construct_tracker(
    tracking: Union[models.FixedTracking, models.SingleAxisTracking]
) -> Tuple[Union[PVSystem, SingleAxisTracker], Dict[str, Any]]:
    """Return the appropriate pvlib.pvsystem class and tracking keywords
    depending on the type of tracking unit"""
    if isinstance(tracking, models.FixedTracking):
        return PVSystem, dict(
            surface_tilt=tracking.tilt, surface_azimuth=tracking.azimuth
        )
    elif isinstance(tracking, models.SingleAxisTracking):
        return SingleAxisTracker, dict(
            axis_tilt=tracking.axis_tilt,
            axis_azimuth=tracking.axis_azimuth,
            gcr=tracking.gcr,
            backtrack=tracking.backtracking,
        )
    else:
        raise TypeError("Only FixedTracking and SingleAxisTracking currently supported")


def construct_pvsystem(inverter: models.Inverter) -> Union[PVSystem, SingleAxisTracker]:
    """Construct a pvlib.pvsystem.PVSystem (or SingleAxisTracker) from an
    Inverter object"""
    # only a single array for now until pvlib#1076
    # otherwise one pvsystem/pvarray per array
    array = inverter.arrays[0]
    common_kwargs = dict(
        albedo=array.albedo,
        module=array.make_model,
        module_parameters=array.module_parameters.dict(),
        temperature_model_parameters=array.temperature_model_parameters.dict(),
        modules_per_string=array.modules_per_string,
        strings_per_inverter=array.strings,
        inverter=inverter.make_model,
        inverter_parameters=inverter.inverter_parameters.dict(),
        name=inverter.name,
    )
    if inverter.losses is not None:
        common_kwargs["losses_parameters"] = inverter.losses.dict()
    system_model, tracking_kwargs = construct_tracker(array.tracking)
    return system_model(**tracking_kwargs, **common_kwargs)


def construct_modelchains(system: models.PVSystem) -> List[ModelChain]:
    """Construct a pvlib.modelchain.ModelChain object for each Inverter
    in system"""
    location = construct_location(system=system)
    out = []
    for inverter in system.inverters:
        pvsystem = construct_pvsystem(inverter=inverter)
        mc = ModelChain(
            system=pvsystem, location=location, **dict(inverter._modelchain_models)
        )
        out.append(mc)
    return out

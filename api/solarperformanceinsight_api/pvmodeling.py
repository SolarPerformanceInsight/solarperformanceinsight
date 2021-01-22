"""Module to translate models.py into pvlib objects and to run the
pvlib models.
"""
from typing import Union, List


from pvlib.location import Location  # type: ignore
from pvlib.modelchain import ModelChain  # type: ignore
from pvlib.pvsystem import PVSystem, Array  # type: ignore
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


def construct_pvsystem(inverter: models.Inverter) -> Union[PVSystem, SingleAxisTracker]:
    """Construct a pvlib.pvsystem.PVSystem (or SingleAxisTracker) from an
    Inverter object"""
    system_kwargs = dict(
        inverter=inverter.make_model,
        inverter_parameters=inverter.inverter_parameters.dict(),
        name=inverter.name,
    )
    if inverter.losses is not None:
        system_kwargs["losses_parameters"] = inverter.losses.dict()

    array_params = []
    tracking_params = []
    is_single_axis = False
    for array in inverter.arrays:
        array_params.append(
            dict(
                albedo=array.albedo,
                module=array.make_model,
                module_parameters=array.module_parameters.dict(),
                temperature_model_parameters=array.temperature_model_parameters.dict(),
                modules_per_string=array.modules_per_string,
                strings=array.strings,
                name=array.name,
            )
        )
        if isinstance(array.tracking, models.SingleAxisTracking):
            tracking_params.append(
                dict(
                    axis_tilt=array.tracking.axis_tilt,
                    axis_azimuth=array.tracking.axis_azimuth,
                    gcr=array.tracking.gcr,
                    backtrack=array.tracking.backtracking,
                )
            )
            is_single_axis = True
            # later might also need to keep track of the array class to use
        else:
            tracking_params.append(
                dict(
                    surface_tilt=array.tracking.tilt,
                    surface_azimuth=array.tracking.azimuth,
                )
            )

    if is_single_axis:
        if len(tracking_params) > 1:  # pragma: no cover
            # until pvlib/pvlib-python#1109 is resolved
            raise ValueError("Single axis tracking with multiple arrays not supported")
        else:
            return SingleAxisTracker(
                arrays=[
                    Array(**array_params[0], surface_tilt=None, surface_azimuth=None)
                ],
                **tracking_params[0],
                **system_kwargs
            )
    else:
        system_kwargs["arrays"] = [
            Array(**atp[0], **atp[1]) for atp in zip(array_params, tracking_params)
        ]
        return PVSystem(**system_kwargs)


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

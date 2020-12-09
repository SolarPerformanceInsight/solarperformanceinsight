from inspect import signature


from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.pvsystem import PVSystem
from pvlib.tracking import SingleAxisTracker
import pytest


from solarperformanceinsight_api import models, pvmodeling


def test_construct_location(system_def):
    # verify that location construction does no input validation
    system_def.longitude = "notanumber"
    assert isinstance(pvmodeling.construct_location(system_def), Location)


@pytest.fixture()
def fixed_tracking():
    return models.FixedTracking(tilt=32, azimuth=180.9)


def test_construct_tracker_fixed(fixed_tracking):
    obj, od = pvmodeling.construct_tracker(fixed_tracking)
    assert obj == PVSystem
    assert od == {"surface_tilt": 32.0, "surface_azimuth": 180.9}


@pytest.fixture()
def single_axis_tracking():
    return models.SingleAxisTracking(
        axis_tilt=0, axis_azimuth=179.8, backtracking=False, gcr=1.8
    )


def test_construct_tracker_single(single_axis_tracking):
    obj, od = pvmodeling.construct_tracker(single_axis_tracking)
    assert obj == SingleAxisTracker
    assert od == {
        "axis_tilt": 0.0,
        "axis_azimuth": 179.8,
        "backtrack": False,
        "gcr": 1.8,
    }


def test_construct_tracker_err(system_def):
    with pytest.raises(TypeError):
        pvmodeling.construct_tracker(system_def)


@pytest.fixture(params=["fixed", "single"])
def either_tracker(request, system_def, fixed_tracking, single_axis_tracking):
    inv = system_def.inverters[0]
    if request.param == "fixed":
        inv.arrays[0].tracking = fixed_tracking
        return inv, PVSystem
    else:
        inv.arrays[0].tracking = single_axis_tracking
        return inv, SingleAxisTracker


def test_construct_pvsystem(either_tracker):
    inv, cls = either_tracker
    out = pvmodeling.construct_pvsystem(inv)
    assert isinstance(out, cls)
    assert isinstance(out.module_parameters, dict)
    assert isinstance(out.temperature_model_parameters, dict)
    assert isinstance(out.inverter_parameters, dict)


def test_construct_pvsystem_consistent_kwargs_fixed(system_def, mocker, fixed_tracking):
    pvsys = mocker.spy(pvmodeling, "PVSystem")
    inv = system_def.inverters[0]
    inv.arrays[0].tracking = fixed_tracking
    out = pvmodeling.construct_pvsystem(inv)
    assert isinstance(out, PVSystem)
    sig = signature(PVSystem)
    params = set(sig.parameters.keys())
    kwargs = set(pvsys.call_args.kwargs.keys())
    assert kwargs.issubset(params)


def test_inverter_models_consistent_with_modelchain(system_def):
    # test Inverter._modelchain_models specifies all _model arguments for ModelChain
    models = {k[0] for k in system_def.inverters[0]._modelchain_models}
    sig = signature(ModelChain)
    model_params = {k for k in sig.parameters.keys() if k.endswith("_model")}
    assert models == model_params


def test_construct_modelchains_fixed(system_def, fixed_tracking):
    system_def.inverters[0].arrays[0].tracking = fixed_tracking
    out = pvmodeling.construct_modelchains(system_def)
    assert len(out) == 1
    assert isinstance(out[0].system, PVSystem)


def test_construct_modelchains_single(system_def, single_axis_tracking):
    system_def.inverters[0].arrays[0].tracking = single_axis_tracking
    out = pvmodeling.construct_modelchains(system_def)
    assert len(out) == 1
    assert isinstance(out[0].system, SingleAxisTracker)

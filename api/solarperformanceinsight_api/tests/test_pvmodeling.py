from inspect import signature


from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.pvsystem import PVSystem
from pvlib.tracking import SingleAxisTracker


from solarperformanceinsight_api import pvmodeling


def test_construct_location(system_def):
    # verify that location construction does no input validation
    system_def.longitude = "notanumber"
    assert isinstance(pvmodeling.construct_location(system_def), Location)


def test_construct_pvsystem(either_tracker):
    inv, cls, multi = either_tracker
    out = pvmodeling.construct_pvsystem(inv)
    assert isinstance(out, cls)
    if multi:
        for mp in out.module_parameters:
            assert isinstance(mp, dict)
        for tmp in out.temperature_model_parameters:
            assert isinstance(tmp, dict)
    else:
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

"""
Retrieve standard sets of parameters
"""
from typing import List

from fastapi import APIRouter, HTTPException, Path
from pvlib.pvsystem import retrieve_sam  # type: ignore


from .. import models


router = APIRouter()
sandia_inverter_params = (
    retrieve_sam("CECInverter")
    .loc[models.SandiaInverterParameters.schema()["properties"].keys()]
    .astype(float)
)

# Database does not provide the fields 'cells_in_series', 'EgRef', 'dEgdT'
# which have defaults in the model.
cec_keys = ["alpha_sc", "a_ref", "I_L_ref", "I_o_ref", "R_sh_ref", "R_s", "Adjust", "N_s"]
cec_module_params = retrieve_sam("CECMod").loc[cec_keys].astype(float).rename(index={"N_s": "cells_in_series"})


@router.get(
    "/sandiainverterparameters",
    response_model=List[str],
    responses={200: {"description": "Names of available Sandia inverters"}},
)
def list_sandia_inverters() -> List[str]:
    """List the names of all Sandia inverters we have parameters for"""
    return sandia_inverter_params.columns.to_list()


@router.get(
    "/sandiainverterparameters/{inverter_name}",
    response_model=models.SandiaInverterParameters,
    responses={200: {}, 404: {}, 422: {}},
    summary="Get a set of SandiaInverterParameters",
)
def get_sandia_inverter(
    inverter_name: str = Path(
        ...,
        description="Name of the inverter to fetch parameters for",
        example="ABB__MICRO_0_25_I_OUTD_US_208__208V_",
    )
) -> models.SandiaInverterParameters:
    """Get the parameters for the named Sandia inverter"""
    if inverter_name not in sandia_inverter_params.columns:
        raise HTTPException(
            status_code=404,
            detail=f"Sandia inverter parameters for {inverter_name} not found",
        )
    return models.SandiaInverterParameters(
        **sandia_inverter_params[inverter_name].to_dict()
    )


@router.get(
    "/cecmoduleparameters",
    response_model=List[str],
    responses={200: {"description": "Names of available CEC(SAM) modules"}},
)
def list_cec_modules() -> List[str]:
    """List the names of all Sandia inverters we have parameters for"""
    return cec_module_params.columns.to_list()


@router.get(
    "/cecmoduleparameters/{module_name}",
    response_model=models.CECModuleParameters,
    responses={200: {}, 404: {}, 422: {}},
    summary="Get a set of CECModuleParameters",
)
def get_cec_module(
    module_name: str = Path(
        ...,
        description="Name of the module to fetch parameters for",
        example="Canadian_Solar_Inc__CS5P_220M",
    )
) -> models.CECModuleParameters:
    """Get the parameters for the named Sandia inverter"""
    if module_name not in cec_module_params.columns:
        raise HTTPException(
            status_code=404,
            detail=f"Module parameters for {module_name} not found",
        )
    return models.CECModuleParameters(
        **cec_module_params[module_name].to_dict()
    )

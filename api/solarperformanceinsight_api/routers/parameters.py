"""
Retrieve standard sets of parameters
"""
from typing import List

from fastapi import APIRouter, HTTPException, Path
from pvlib.pvsystem import retrieve_sam  # type: ignore
import pytz


from .. import models


router = APIRouter()
sandia_inverter_params = (
    retrieve_sam("CECInverter")
    .loc[models.SandiaInverterParameters.schema()["properties"].keys()]
    .astype(float)
)


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


@router.get("/timezones", response_model=List[str])
def get_timezones() -> List[str]:
    """Get all recognized timezones"""
    return pytz.all_timezones

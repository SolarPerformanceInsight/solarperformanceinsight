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


@router.get(
    "/inverters/sandia/",
    response_model=List[str],
    responses={200: {"description": "Names of available Sandia inverters"}},
)
def get_sandia_inverters() -> List[str]:
    return sandia_inverter_params.columns.to_list()


@router.get(
    "/inverters/sandia/{inverter_name}",
    response_model=models.SandiaInverterParameters,
    responses={200: {}, 404: {}, 422: {}},
)
def get_one_sandia_inverter(
    inverter_name: str = Path(
        ...,
        description="Name of the inverter to fetch parameters for",
        example="ABB__MICRO_0_25_I_OUTD_US_208__208V_",
    )
) -> models.SandiaInverterParameters:
    if inverter_name not in sandia_inverter_params.columns:
        raise HTTPException(
            status_code=404,
            detail=f"Sandia inverter parameters for {inverter_name} not found",
        )
    return models.SandiaInverterParameters(
        **sandia_inverter_params[inverter_name].to_dict()
    )

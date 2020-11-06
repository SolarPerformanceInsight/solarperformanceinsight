from typing import List
from fastapi import APIRouter


from ..models import PVSystem


router = APIRouter()


@router.get("/", response_model=List[PVSystem])
async def list_plants():
    """These docs show up on openapi

    \f
    This does not show up on openapi

    Raises
    -------
    whatever
    """
    return


@router.get("/{plant_id}", response_model=PVSystem)
async def get_plant(plant_id: str):
    return


@router.post("/")
async def create_plant(system: PVSystem):
    return

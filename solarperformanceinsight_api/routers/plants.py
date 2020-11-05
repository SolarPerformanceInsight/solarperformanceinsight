from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def list_plants():
    """These docs show up on openapi

    \f
    This does not show up on openapi

    Raises
    -------
    whatever
    """
    return

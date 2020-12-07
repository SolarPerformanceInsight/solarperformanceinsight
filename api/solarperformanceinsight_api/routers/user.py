from fastapi import APIRouter, Depends


from . import default_get_responses
from .. import models
from ..storage import StorageInterface


router = APIRouter()


@router.get("/", response_model=models.UserInfo, responses=default_get_responses)
async def get_user_info(
    storage: StorageInterface = Depends(StorageInterface),
) -> models.UserInfo:
    """Get info about the current user"""
    with storage.start_transaction() as st:
        out = st.get_user()
        return out

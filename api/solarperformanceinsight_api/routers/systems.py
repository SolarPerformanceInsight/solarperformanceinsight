from typing import List
from fastapi import APIRouter, Response, Request, Depends
from pydantic.types import UUID


from . import default_get_responses
from .. import models
from ..storage import StorageInterface


router = APIRouter()


@router.get(
    "/", response_model=List[models.StoredPVSystem], responses=default_get_responses
)
async def list_systems(
    storage: StorageInterface = Depends(StorageInterface),
) -> List[models.StoredPVSystem]:
    """List available PV systems"""
    with storage.start_transaction() as st:
        out = st.list_systems()
        return out


system_links = {
    "Get System": {
        "operationId": "get_system_systems__system_id__get",
        "parameters": {"system_id": "$response.body#/object_id"},
    },
    "Delete System": {
        "operationId": "delete_system_systems__system_id__delete",
        "parameters": {"system_id": "$response.body#/object_id"},
    },
    "Update System": {
        "operationId": "update_system_systems__system_id__post",
        "parameters": {"system_id": "$response.body#/object_id"},
    },
}


@router.post(
    "/",
    response_model=models.StoredObjectID,
    responses={
        **default_get_responses,
        409: {},
        201: {"links": system_links},
    },
    status_code=201,
)
async def create_system(
    system: models.PVSystem,
    response: Response,
    request: Request,
    storage: StorageInterface = Depends(StorageInterface),
) -> models.StoredObjectID:
    """Create a new PV System"""
    with storage.start_transaction() as st:
        id_ = st.create_system(system)
        response.headers["Location"] = request.url_for(
            "get_system", system_id=id_.object_id
        )
        return id_


@router.post(
    "/check",
    responses={401: {}, 403: {}},
    status_code=200,
)
async def check_system(
    system: models.PVSystem,
):
    """Check if the POSTed system is valid for modeling"""
    return


@router.get(
    "/{system_id}",
    response_model=models.StoredPVSystem,
    responses={
        **default_get_responses,
        200: {"links": system_links},
    },
)
async def get_system(
    system_id: UUID, storage: StorageInterface = Depends(StorageInterface)
) -> models.StoredPVSystem:
    """Get a single PV System"""
    with storage.start_transaction() as st:
        return st.get_system(system_id)


@router.delete(
    "/{system_id}", responses={**default_get_responses, 204: {}}, status_code=204
)
async def delete_system(
    system_id: UUID, storage: StorageInterface = Depends(StorageInterface)
):
    """Delete a PV system"""
    with storage.start_transaction() as st:
        st.delete_system(system_id)


@router.post(
    "/{system_id}",
    response_model=models.StoredObjectID,
    responses={
        **default_get_responses,
        201: {"links": system_links},
    },
    status_code=201,
)
async def update_system(
    system_id: UUID,
    system: models.PVSystem,
    response: Response,
    request: Request,
    storage: StorageInterface = Depends(StorageInterface),
) -> models.StoredObjectID:
    """Update a PV System"""
    with storage.start_transaction() as st:
        out = st.update_system(system_id, system)
        response.headers["Location"] = request.url_for(
            "get_system", system_id=system_id
        )
        return out

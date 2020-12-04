import datetime as dt
import random
import uuid


from typing import List
from fastapi import APIRouter, HTTPException, Response, Request
from pydantic.types import UUID


from . import default_get_responses
from .. import models


router = APIRouter()


def _gen_uuid():
    return uuid.uuid1(
        node=random.SystemRandom().getrandbits(48),
        clock_seq=random.SystemRandom().getrandbits(14),
    )


PVSYSTEMS = {
    uuid.UUID("6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9"): models.StoredPVSystem(
        object_id=uuid.UUID("6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9"),
        created_at="2020-12-01T01:23:00+00:00",
        modified_at="2020-12-01T01:23:00+00:00",
        definition=models.SYSTEM_EXAMPLE,
    )
}


@router.get(
    "/", response_model=List[models.StoredPVSystem], responses=default_get_responses
)
async def list_systems():
    """List available PV systems"""
    return list(PVSYSTEMS.values())


@router.post(
    "/",
    response_model=models.StoredPVSystem,
    responses={
        **default_get_responses,
        201: {
            "links": {
                "Get System": {
                    "operationId": "get_system_systems__system_id__get",
                    "parameters": {"system_id": "$response.body#/object_id"},
                }
            }
        },
    },
    status_code=201,
)
async def create_system(system: models.PVSystem, response: Response, request: Request):
    """Create a new PV System"""
    global PVSYSTEMS
    id_ = _gen_uuid()
    now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc, microsecond=0)
    created = models.StoredPVSystem(
        object_id=id_, created_at=now, modified_at=now, definition=system
    )
    PVSYSTEMS[id_] = created
    response.headers["Location"] = request.url_for("get_system", system_id=id_)
    return created


@router.get(
    "/{system_id}",
    response_model=models.StoredPVSystem,
    responses=default_get_responses,
)
async def get_system(system_id: UUID):
    if system_id in PVSYSTEMS:
        return PVSYSTEMS[system_id]
    else:
        raise HTTPException(status_code=404)

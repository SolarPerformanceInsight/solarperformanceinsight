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
        system_id=uuid.UUID("6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9"),
        created_at="2020-12-01T01:23:00+00:00",
        modified_at="2020-12-01T01:23:00+00:00",
        definition=models.PVSystem(
            name="Test PV System",
            latitude=33.98,
            longitude=-115.323,
            elevation=2300,
            albedo=0.2,
            inverters=[
                models.Inverter(
                    name="Inverter 1",
                    make_model="ABB__MICRO_0_25_I_OUTD_US_208__208V_",
                    inverter_parameters=models.SandiaInverterParameters(
                        Pso=2.08961,
                        Paco=250,
                        Pdco=259.589,
                        Vdco=40,
                        C0=-4.1e-05,
                        C1=-9.1e-05,
                        C2=0.000494,
                        C3=-0.013171,
                        Pnt=0.075,
                    ),
                    losses={},
                    arrays=[
                        models.PVArray(
                            name="Array 1",
                            make_model="Canadian_Solar_Inc__CS5P_220M",
                            modules_per_string=7,
                            strings=5,
                            tracking=models.FixedTracking(
                                tilt=20.0,
                                azimuth=180.0,
                            ),
                            temperature_model_parameters=models.PVsystTemperatureParameters(),  # NOQA: E501
                            module_parameters=models.PVsystModuleParameters(
                                alpha_sc=0.004539,
                                gamma_ref=1.2,
                                mu_gamma=-0.003,
                                I_L_ref=5.11426,
                                I_o_ref=8.10251e-10,
                                R_sh_ref=381.254,
                                R_s=1.06602,
                                R_sh_0=400.0,
                                cells_in_series=96,
                            ),
                        )
                    ],
                ),
            ],
        ),
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
                    "parameters": {"system_id": "$response.body#/system_id"},
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
        system_id=id_, created_at=now, modified_at=now, definition=system
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

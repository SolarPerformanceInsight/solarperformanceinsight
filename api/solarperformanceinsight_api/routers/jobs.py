"""Endpoints for running models"""
import logging
from typing import List


from fastapi import (
    APIRouter,
    Response,
    Request,
    Depends,
    UploadFile,
    File,
    HTTPException,
)
from pydantic.types import UUID


from . import default_get_responses
from .. import models, utils
from ..storage import StorageInterface


logger = logging.getLogger(__name__)
router = APIRouter()


job_links = {
    "Get Job": {
        "operationId": "get_job_jobs__job_id__get",
        "parameters": {"job_id": "$response.body#/object_id"},
    },
    "Delete Job": {
        "operationId": "delete_job_jobs__job_id__delete",
        "parameters": {"job_id": "$response.body#/object_id"},
    },
    "Get Job Status": {
        "operationId": "get_job_status_jobs__job_id__status_get",
        "parameters": {"job_id": "$response.body#/object_id"},
    },
    "Get Job Results": {
        "operationId": "get_job_results_jobs__job_id__results_get",
        "parameters": {"job_id": "$response.body#/object_id"},
    },
    "Compute Job": {
        "operationId": "compute_job_jobs__job_id__compute_post",
        "parameters": {"job_id": "$response.body#/object_id"},
    },
}


@router.post(
    "/",
    response_model=models.StoredObjectID,
    responses={
        **default_get_responses,
        409: {},
        201: {"links": job_links},
    },
    status_code=201,
)
async def create_job(
    job_parameters: models.JobParameters,
    response: Response,
    request: Request,
    storage: StorageInterface = Depends(StorageInterface),
) -> models.StoredObjectID:
    """Create a new job"""
    with storage.start_transaction() as st:
        system = st.get_system(job_parameters.system_id)
        job = models.Job(system_definition=system.definition, parameters=job_parameters)
        id_ = st.create_job(job)
        response.headers["Location"] = request.url_for("get_job", job_id=id_.object_id)
        return id_


@router.post("/check", responses={201: {}, 401: {}, 403: {}, 422: {}}, status_code=201)
async def check_job(job: models.JobParameters):  # pragma: no cover
    pass


@router.get("/", response_model=List[models.StoredJob], responses=default_get_responses)
async def list_jobs(
    storage: StorageInterface = Depends(StorageInterface),
) -> List[models.StoredJob]:
    with storage.start_transaction() as st:
        return st.list_jobs()


@router.get(
    "/{job_id}",
    response_model=models.StoredJob,
    responses={**default_get_responses, 200: {"links": job_links}},
)
async def get_job(
    job_id: UUID, storage: StorageInterface = Depends(StorageInterface)
) -> models.StoredJob:
    with storage.start_transaction() as st:
        return st.get_job(job_id)


@router.get(
    "/{job_id}/status", response_model=models.JobStatus, responses=default_get_responses
)
async def get_job_status(
    job_id: UUID, storage: StorageInterface = Depends(StorageInterface)
) -> models.JobStatus:
    with storage.start_transaction() as st:
        return st.get_job_status(job_id)


@router.delete(
    "/{job_id}", status_code=204, responses={**default_get_responses, 204: {}}
)
async def delete_job(
    job_id: UUID, storage: StorageInterface = Depends(StorageInterface)
):
    with storage.start_transaction() as st:
        st.delete_job(job_id)


class ArrowResponse(Response):
    media_type = "application/vnd.apache.arrow.file"


@router.get(
    "/{job_id}/data/{data_id}",
    response_class=ArrowResponse,
    responses=default_get_responses,
)
async def get_job_data(
    job_id: UUID, data_id: UUID, storage: StorageInterface = Depends(StorageInterface)
):
    with storage.start_transaction() as st:
        meta, data = st.get_job_data(job_id, data_id)
        # check data type?
    return ArrowResponse(data)


@router.post(
    "/{job_id}/data/{data_id}",
    status_code=204,
    responses={**default_get_responses, 204: {}, 415: {}},
)
async def post_job_data(
    job_id: UUID,
    data_id: UUID,
    file: UploadFile = File(
        ..., description="A single file in the Apache Arrow file format"
    ),
    storage: StorageInterface = Depends(StorageInterface),
):
    read_fnc = utils.verify_content_type(file.content_type)
    with storage.start_transaction() as st:
        job = st.get_job(job_id)
    try:
        data_obj = list(filter(lambda x: x.object_id == data_id, job.data_objects))[0]
    except IndexError:
        raise HTTPException(status_code=404, detail="Job data upload denied")
    expected_columns = data_obj.definition.data_columns
    df = read_fnc(file.file)
    await file.close()
    utils.validate_dataframe(df, expected_columns)
    # will fail w/o time column
    df, extra_times, missing_times = utils.reindex_timeseries(
        df, job.definition.parameters.time_parameters
    )
    # if missing > len(df) * .1 raise? or raise if any extra/missing?
    arrow_bytes = utils.dump_arrow_bytes(utils.convert_to_arrow(df))
    with storage.start_transaction() as st:
        st.add_job_data(
            job_id,
            data_id,
            file.filename,
            "application/vnd.apache.arrow.file",
            arrow_bytes,
        )
    # more informative like how many valid rows, how many nan vals,
    # how many inserted nans


@router.post(
    "/{job_id}/compute", status_code=202, responses={**default_get_responses, 202: {}}
)
async def compute_job(
    job_id: UUID,
    storage: StorageInterface = Depends(StorageInterface),
):
    with storage.start_transaction() as st:
        st.queue_job(job_id)


@router.get("/{job_id}/results", responses=default_get_responses)
async def get_job_results(job_id: UUID):  # pragma: no cover
    pass

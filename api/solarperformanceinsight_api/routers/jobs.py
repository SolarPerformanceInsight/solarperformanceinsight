"""Endpoints for running models"""
from typing import List


from fastapi import APIRouter, Response, Request, Depends, UploadFile, File
from pydantic.types import UUID


from . import default_get_responses
from .. import models
from ..storage import StorageInterface


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


@router.post("/check", responses={200: {}, 401: {}, 403: {}, 422: {}}, status_code=200)
async def check_job(job: models.JobParameters):
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
        meta, data = st.get_job_data(data_id)
        # check job_id?
        # check data type?
    return ArrowResponse(data)


@router.post(
    "/{job_id}/data/{data_id}",
    status_code=204,
    responses={**default_get_responses, 204: {}},
)
async def post_job_data(
    job_id: UUID,
    data_id: UUID,
    file: UploadFile = File(
        ..., description="A single file in the Apache Arrow file format"
    ),
    storage: StorageInterface = Depends(StorageInterface),
):
    # check and reject content type
    # check columns conform
    content = await file.read()
    await file.close()
    with storage.start_transaction() as st:
        st.add_job_data(data_id, file.filename, file.content_type, content)


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
async def get_job_results(job_id: UUID):
    pass

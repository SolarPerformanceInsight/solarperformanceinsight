"""Endpoints for running models"""
import logging
from typing import List, Optional, Union, Type, Tuple


from accept_types import AcceptableType  # type: ignore
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Response,
    Request,
    Depends,
    UploadFile,
    File,
    Header,
    HTTPException,
)
import pandas as pd
from pydantic.types import UUID


from . import default_get_responses
from .. import models, utils
from ..auth import get_user_id
from ..storage import StorageInterface
from ..queuing import QueueManager


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
    response: Response,
    request: Request,
    job_parameters: models.JobParametersType = Body(
        ..., example=models.JOB_PARAMS_EXAMPLE
    ),
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
async def check_job(
    job_parameters: models.JobParametersType = Body(
        ..., example=models.JOB_PARAMS_EXAMPLE
    ),
):
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
    job_id: UUID,
    storage: StorageInterface = Depends(StorageInterface),
    qm: QueueManager = Depends(QueueManager),
) -> models.JobStatus:
    with storage.start_transaction() as st:
        db_status = st.get_job_status(job_id)
    if db_status.status == "queued":
        q_status = qm.job_status(job_id)
        if q_status is not None:
            return q_status
    return db_status


@router.delete(
    "/{job_id}", status_code=204, responses={**default_get_responses, 204: {}}
)
async def delete_job(
    job_id: UUID,
    background_tasks: BackgroundTasks,
    storage: StorageInterface = Depends(StorageInterface),
    qm: QueueManager = Depends(QueueManager),
):
    with storage.start_transaction() as st:
        st.delete_job(job_id)
    background_tasks.add_task(qm.delete_job, job_id)


class ArrowResponse(Response):
    media_type = "application/vnd.apache.arrow.file"


class CSVResponse(Response):
    media_type = "text/csv"


def _get_return_type(
    accept: Optional[str],
) -> Tuple[Union[Type[CSVResponse], Type[ArrowResponse]], str]:
    if accept is None:
        accept = "*/*"
    type_ = AcceptableType(accept)

    if type_.matches("text/csv"):
        return CSVResponse, "text/csv"
    elif type_.matches("application/vnd.apache.arrow.file"):
        return ArrowResponse, "application/vnd.apache.arrow.file"
    else:
        raise HTTPException(
            status_code=406,
            detail="Only 'text/csv' or 'application/vnd.apache.arrow.file' acceptable",
        )


@router.get(
    "/{job_id}/data/{data_id}",
    response_class=CSVResponse,
    responses={
        **default_get_responses,
        406: {},
        204: {"description": "Data object exists but no data has been uploaded."},
        200: {
            "content": {
                "application/vnd.apache.arrow.file": {},
                "text/csv": {
                    "example": """time,performance
2020-01-01 00:00:00+00:00,0
2020-01-01 01:00:00+00:00,1
"""
                },
            },
            "description": "Return the data as an Apache Arrow file or a CSV.",
        },
    },
)
async def get_job_data(
    job_id: UUID,
    data_id: UUID,
    storage: StorageInterface = Depends(StorageInterface),
    accept: Optional[str] = Header(None),
) -> Union[CSVResponse, ArrowResponse, Response]:
    resp, meta_type = _get_return_type(accept)
    with storage.start_transaction() as st:
        meta, data = st.get_job_data(job_id, data_id)
    if not meta.definition.present or len(data) == 0:
        return Response(status_code=204)
    return _convert_job_data(data, meta.definition.data_format, meta_type, resp)


def _convert_job_data(data, data_format, requested_mimetype, response_class):
    if requested_mimetype == data_format:
        return response_class(data)
    elif (
        data_format == "application/vnd.apache.arrow.file"
        and requested_mimetype == "text/csv"
    ):
        try:
            df = utils.read_arrow(data)
        except HTTPException:
            logger.exception("Read arrow failed")
            raise HTTPException(
                status_code=500,
                detail=(
                    "Unable to convert data saved as Apache Arrow format, "
                    "try retrieving as application/vnd.apache.arrow.file and converting"
                ),
            )
        csv = df.to_csv(None, index=False)
        return response_class(csv)
    else:
        raise HTTPException(
            status_code=400,
            detail=(f"Unable to convert from {data_format} to {requested_mimetype}"),
        )


@router.post(
    "/{job_id}/data/{data_id}",
    responses={**default_get_responses, 415: {}},
    response_model=models.DataParsingStats,
)
async def post_job_data(
    job_id: UUID,
    data_id: UUID,
    file: UploadFile = File(
        ...,
        description=(
            "A single file in CSV format or Apache Arrow file format (default). "
            "Specify the Content-Type of the file as either 'text/csv' or "
            "'application/vnd.apache.arrow.file' as appropriate. Files with a "
            "Content-Type of 'application/octet-stream' (curl default) will be "
            "parsed as if they are Apache Arrow files."
        ),
    ),
    storage: StorageInterface = Depends(StorageInterface),
) -> models.DataParsingStats:
    """Upload specified data for the job. If the upload is of
    predicted/original weather or performance, an attempt will be made to
    shift the data by whole years to match the time range specified for
    the job. Use this functionality with caution."""
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
    if isinstance(
        job.definition.parameters, models.CompareMonthlyPredictedActualJobParameters
    ):
        adjusted_df, data_stats = _adjust_monthly_series(df)
    else:
        allow_time_shift = data_obj.definition.type in (
            models.JobDataTypeEnum.original_weather,
            models.JobDataTypeEnum.predicted_performance,
            models.JobDataTypeEnum.predicted_performance_dc,
        )
        adjusted_df, data_stats = _adjust_standard_timeseries(
            job, df, expected_columns, allow_time_shift
        )
    arrow_bytes = utils.dump_arrow_bytes(utils.convert_to_arrow(adjusted_df))
    with storage.start_transaction() as st:
        st.add_job_data(
            job_id,
            data_id,
            file.filename,
            "application/vnd.apache.arrow.file",
            arrow_bytes,
        )
    return data_stats


def _adjust_monthly_series(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, models.DataParsingStats]:
    df = utils.standardize_months(df)
    stats = models.DataParsingStats(
        number_of_expected_rows=12,
        number_of_extra_rows=0,
        number_of_missing_rows=0,
        data_periods=dict(expected="monthly", uploaded="monthly"),
        extra_times=[],
        missing_times=[],
        number_of_missing_values=[],
    )
    return df, stats


def _adjust_standard_timeseries(
    job: models.StoredJob,
    df: pd.DataFrame,
    expected_columns: List[str],
    allow_time_shift: bool,
) -> Tuple[pd.DataFrame, models.DataParsingStats]:
    try:
        uploaded_period = str(
            pd.tseries.frequencies.to_offset(  # type: ignore
                df["time"].diff().mode().iloc[0]  # type: ignore
            )
        )
    except Exception:  # pragma: no cover
        uploaded_period = "Unknown"
    time_params: models.JobTimeindex = (
        job.definition.parameters.time_parameters  # type: ignore
    )
    periods = models.DataPeriods(
        expected=str(time_params._time_range.freq),  # type: ignore
        uploaded=uploaded_period,
    )

    # will fail w/o time column
    df, extra_times, missing_times = utils.reindex_timeseries(
        df, time_params, allow_time_shift
    )
    percent_missing = len(missing_times) / len(df.index) * 100
    if percent_missing > 10:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Over {percent_missing:0.2f}% of rows were missing from the "
                "data upload to conform to the job's stated time index."
            ),
        )
    dft = df[expected_columns].set_index("time")
    missing_vals = (
        dft.loc[dft.index.difference(missing_times)]  # type: ignore
        .isna()
        .sum(axis=0)
        .to_dict()
    )
    return (
        df,
        models.DataParsingStats(
            number_of_expected_rows=len(df.index),
            number_of_extra_rows=len(extra_times),
            number_of_missing_rows=len(missing_times),
            data_periods=periods,
            extra_times=extra_times,
            missing_times=missing_times,
            number_of_missing_values=missing_vals,
        ),
    )


@router.post(
    "/{job_id}/compute", status_code=202, responses={**default_get_responses, 202: {}}
)
async def compute_job(
    job_id: UUID,
    background_tasks: BackgroundTasks,
    storage: StorageInterface = Depends(StorageInterface),
    user: str = Depends(get_user_id),
    qm: QueueManager = Depends(QueueManager),
):
    with storage.start_transaction() as st:
        st.queue_job(job_id)
    background_tasks.add_task(qm.enqueue_job, job_id, user)


@router.get(
    "/{job_id}/results",
    responses=default_get_responses,
    response_model=List[models.StoredJobResultMetadata],
)
async def list_job_results(
    job_id: UUID,
    storage: StorageInterface = Depends(StorageInterface),
):
    with storage.start_transaction() as st:
        return st.list_job_results(job_id)


@router.get(
    "/{job_id}/results/{result_id}",
    responses={
        **default_get_responses,
        406: {},
        200: {
            "content": {
                "application/vnd.apache.arrow.file": {},
                "text/csv": {
                    "example": """time,performance
2020-01-01 00:00:00+00:00,0
2020-01-01 01:00:00+00:00,1
"""
                },
                "application/json": {},
            },
            "description": (
                "Return the job result as an Apache Arrow file or a CSV."
                " If an error occured, this will always return application/json"
                " with further details."
            ),
        },
    },
)
async def get_job_result(
    job_id: UUID,
    result_id: UUID,
    storage: StorageInterface = Depends(StorageInterface),
    accept: Optional[str] = Header(None),
) -> Union[CSVResponse, ArrowResponse, Response]:
    # once queing is figured out, this will need to also probably
    # return JSON describing any errors
    resp, meta_type = _get_return_type(accept)
    with storage.start_transaction() as st:
        meta, data = st.get_job_result(job_id, result_id)
    if meta.definition.type == models.JobResultTypeEnum.error:
        return Response(content=data, media_type=meta.definition.data_format)
    return _convert_job_data(data, meta.definition.data_format, meta_type, resp)

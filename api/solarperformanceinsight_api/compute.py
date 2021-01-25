import json
import logging
from typing import Callable
from uuid import UUID


from fastapi import HTTPException


from . import storage, models


logger = logging.getLogger(__name__)


def run_job(job_id: UUID, user: str):
    si = storage.StorageInterface(user=user)
    try:
        with si.start_transaction() as st:
            job = st.get_job(job_id)
    except HTTPException as err:
        if err.status_code == 404:
            # job doesn't exist or can't be fetched, so no point continuing
            return
        else:  # pragma: no cover
            raise

    job_func = lookup_job_compute_function(job)
    try:
        job_func(job, si)
    except Exception as err:
        logger.exception("Error for job %s", job_id)
        with si.start_transaction() as st:
            st.add_job_result(
                job_id,
                "/",
                "error message",
                "application/json",
                json.dumps({"error": {"details": err.args[0]}}),
            )
            st.set_job_error(job_id)


def lookup_job_compute_function(
    job: models.StoredJob,
) -> Callable[[models.StoredJob, storage.StorageInterface], None]:
    return dummy_func


def dummy_func(job, storage):
    raise NotImplementedError("Job computation not implemented")

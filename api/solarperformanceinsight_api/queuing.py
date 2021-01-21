import datetime as dt
import json
import logging
from typing import Union, Type, Dict, Tuple, List
from uuid import UUID


from redis import Redis, ConnectionPool
from rq import Queue  # type: ignore
from rq.command import send_stop_job_command  # type: ignore
from rq.exceptions import NoSuchJobError  # type: ignore
from rq.job import Job  # type: ignore


from . import settings, compute, models


logger = logging.getLogger(__name__)
redis_pool = ConnectionPool(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    username=settings.redis_username,
    password=settings.redis_password,
    health_check_interval=settings.redis_health_check_interval,
)


def _get_redis_conn():  # pragma: no cover
    # easier mocking of redis
    return Redis(connection_pool=redis_pool)


def verify_redis_conn():
    redis_conn = _get_redis_conn()
    return redis_conn.ping()


def _get_queue(name, redis_conn):
    return Queue(name, connection=redis_conn)


class QueueManager:
    def __init__(
        self,
        queue_name: str = "jobs",
    ):
        self.redis_conn = _get_redis_conn()
        self.q = _get_queue(queue_name, self.redis_conn)
        self.job_func = compute.run_job

    @property
    def registries(self):
        return [
            getattr(self.q, reg)
            for reg in (
                "started_job_registry",
                "deferred_job_registry",
                "finished_job_registry",
                "failed_job_registry",
                "scheduled_job_registry",
            )
        ]

    def enqueue_job(self, job_id: Union[UUID, str], user: str) -> Type[Job]:
        # check if job already exists
        try:
            job = Job.fetch(str(job_id), connection=self.redis_conn)
        except NoSuchJobError:
            job = Job.create(
                self.job_func,
                args=(job_id, user),
                id=str(job_id),
                result_ttl=10,
                timeout="10m",
                failure_ttl=3600 * 24 * 14,
                connection=self.redis_conn,
            )
            self.q.enqueue_job(job)
        return job

    def job_status(self, job_id: UUID) -> Union[models.JobStatus, None]:
        """Return a "running" status and the start time of a job. Even a
        failed job will report "running" as the failure may need to be added
        to the database for retrieval."""
        try:
            job = Job.fetch(str(job_id), connection=self.redis_conn)
        except NoSuchJobError:
            pass
        else:
            if job.started_at is not None:
                # rq stores time as utc
                change_time = job.started_at.replace(tzinfo=dt.timezone.utc)
                return models.JobStatus(status="running", last_change=change_time)
        return None

    def delete_job(self, job_id: UUID):
        """Try removing the job if present in any registries"""
        try:
            send_stop_job_command(self.redis_conn, str(job_id))
        except Exception:
            pass
        for registry in self.registries:
            try:
                registry.remove(str(job_id), delete_job=True)
            except Exception:
                pass

    def remove_invalid_jobs(self, current_job_status: Dict[str, str]):
        """Remove jobs from any queue that are complete or have been
        deleted from the database"""
        all_jobs = current_job_status.keys()
        jobs_to_remove_if_present = [
            k for k, v in current_job_status.items() if v != "queued"
        ]
        i = 0
        for job_id in self.q.job_ids:
            if job_id not in all_jobs or job_id in jobs_to_remove_if_present:
                self.delete_job(job_id)
                i += 1
        logger.info("Removed %s invalid jobs from the queues", i)

    def add_missing_jobs(self, queued_jobs: Dict[str, str]):
        """Add jobs to the queue that are missing but present in the database
        and not complete"""
        missing = set(queued_jobs.keys()) - set(self.q.job_ids)
        logger.info("Enqueuing %s missing jobs", len(missing))
        for id_ in missing:
            self.enqueue_job(id_, queued_jobs[id_])

    def evaluate_failed_jobs(
        self, current_job_status: Dict[str, str]
    ) -> List[Tuple[str, str]]:
        """If job has gotten to the failed job registry, some uncaught error
        happened.
        of job ids and failure messages"""
        out = []
        for failed_job in self.q.failed_job_registry.get_job_ids():
            if failed_job not in current_job_status or current_job_status[
                failed_job
            ] in ("complete", "error"):
                self.q.failed_job_registry.remove(failed_job, delete_job=True)
            else:
                msg = json.dumps(
                    {
                        "error": {
                            "details": (
                                "Uncaught error during job execution. "
                                "Framework administrators have been notified."
                            )
                        }
                    }
                )
                out.append((failed_job, msg))
        logger.info("%s jobs processed from failed job registry", len(out))
        return out

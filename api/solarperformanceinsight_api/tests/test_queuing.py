import pytest
from rq import Queue, get_current_job, SimpleWorker
from rq.exceptions import NoSuchJobError
from rq.job import Job


from solarperformanceinsight_api import queuing


pytestmark = pytest.mark.usefixtures("mock_redis")


def test_verify_redis_conn():
    assert queuing.verify_redis_conn()


def run(job_id, user):
    job = get_current_job()
    # started_at not set when using sync queue
    job.started_at = job.enqueued_at
    return job_id, user


@pytest.fixture()
def qm():
    out = queuing.QueueManager()
    out.job_func = run
    q = Queue(is_async=False, connection=out.redis_conn)
    out.q = q
    return out


def test_qmanager_enqueue_job(qm):
    job = qm.enqueue_job("jobid", "user")
    assert job.is_finished
    assert job.result == ("jobid", "user")
    assert job.id == "jobid"

    # if enqueued multiple times, only get first job
    job2 = qm.enqueue_job("jobid", "newuser")
    assert job2 == job


def test_qmanager_job_status(qm):
    assert qm.job_status("jobid") is None
    qm.enqueue_job("jobid", "user")
    stat = qm.job_status("jobid")
    assert stat is not None
    assert stat.status == "running"


def test_qmanager_delete_job(qm):
    qm.enqueue_job("jobid", "user")
    qm.delete_job("jobid")
    with pytest.raises(NoSuchJobError):
        Job.fetch("jobid", connection=qm.redis_conn)


def test_qmanager_remove_invalid_jobs():
    qm = queuing.QueueManager()
    qm.job_func = run
    job_status = {
        "0": "complete",
        "1": "created",
        "2": "queued",
        "3": "queued",
        "4": "error",
    }
    for i in range(10):
        qm.enqueue_job(str(i), "user")
    assert qm.q.job_ids == [str(i) for i in range(10)]
    qm.remove_invalid_jobs(job_status)
    assert qm.q.job_ids == ["2", "3"]


def test_qmanager_add_missing_jobs():
    qm = queuing.QueueManager()
    qm.job_func = run
    queued = {str(i): "user" for i in range(5)}
    qm.enqueue_job("0", "user")
    qm.enqueue_job("4", "user")
    assert qm.q.job_ids == ["0", "4"]
    qm.add_missing_jobs(queued)
    assert set(qm.q.job_ids) == {str(i) for i in range(5)}


def fail(err, msg):
    raise err(msg)


def ok():
    pass


def test_qmanager_evaluate_failed_jobs():
    qm = queuing.QueueManager()
    qm.job_func = fail
    assert len(qm.q.failed_job_registry) == 0
    qm.q.enqueue(fail, ValueError, "0 isnt 1", job_id="0")
    qm.q.enqueue(ok, job_id="1")
    qm.q.enqueue(fail, TypeError, "wrong type", job_id="2")
    w = SimpleWorker([qm.q], connection=qm.redis_conn)
    w.work(burst=True)
    assert len(qm.q.failed_job_registry) == 2

    job_status = {
        "0": "queued",
        "1": "queued",
        "3": "queued",
        "4": "error",
        "5": "complete",
        "6": "created",
    }
    out = qm.evaluate_failed_jobs(job_status)
    assert len(out) == 1
    assert out[0][0] == "0"


def test_sync_jobs(mocker):
    qm = queuing.QueueManager()
    qm.job_func = run
    job_status = {
        "0": "queued",
        "1": "queued",
        "3": "queued",
    }
    qm.q.enqueue(fail, ValueError, "0 isnt 1", job_id="0")
    w = SimpleWorker([qm.q], connection=qm.redis_conn)
    w.work(burst=True)
    assert len(qm.q.failed_job_registry) == 1

    queued = {str(i): "user" for i in range(5)}
    qm.enqueue_job("4", "user")
    assert qm.q.job_ids == ["4"]

    mocker.patch(
        "solarperformanceinsight_api.queuing.time.sleep", side_effect=KeyboardInterrupt
    )

    jmi = mocker.MagicMock()
    startt = jmi.start_transaction.return_value.__enter__.return_value
    startt.list_queued_jobs.return_value = queued
    startt.list_status_of_jobs.return_value = job_status
    mocker.patch(
        "solarperformanceinsight_api.queuing._get_job_management_interface",
        return_value=jmi,
    )
    queuing.sync_jobs()
    # 0 failed, 2 is missing
    assert set(qm.q.job_ids) == {"1", "3"}
    assert startt.report_job_failure.call_count == 1

def test_list_status_of_jobs(dictcursor, job_id, other_job_id):
    dictcursor.execute(
        "update jobs set status = 'error' where id = uuid_to_bin(%s, 1)", other_job_id
    )
    dictcursor.execute("call list_status_of_jobs()")
    out = dictcursor.fetchall()
    assert out == [
        {"job_id": job_id, "status": "created"},
        {"job_id": other_job_id, "status": "error"},
    ]


def test_list_queued_jobs(dictcursor, job_id, other_job_id, auth0_id):
    dictcursor.execute(
        "update jobs set status = 'queued' where id = uuid_to_bin(%s, 1)", other_job_id
    )
    dictcursor.execute("call list_queued_jobs()")
    out = dictcursor.fetchall()
    assert out == [{"job_id": other_job_id, "user_id": auth0_id}]


def test_report_job_failure(dictcursor, job_id):
    msg = '{"error":{"detail": "it failed"}}'
    dictcursor.execute("call report_job_failure(%s, %s)", (job_id, msg))
    jid = dictcursor.fetchone()["result_id"]
    dictcursor.execute("select status from jobs where id = uuid_to_bin(%s, 1)", job_id)
    assert dictcursor.fetchone()["status"] == "error"
    dictcursor.execute(
        "select data from job_results where id = uuid_to_bin(%s, 1)", jid
    )
    dictcursor.fetchone()["data"] == msg

-- migrate:up
create user if not exists 'qmanager'@'%' identified with caching_sha2_password by 'terriblepasswordtochange';

create definer = 'select_objects'@'localhost'
  procedure list_status_of_jobs()
    comment 'List all jobs that have queued status'
    reads sql data sql security definer
  begin
    select bin_to_uuid(id, 1) as job_id, status from jobs;
  end;

grant execute on procedure `list_status_of_jobs` to 'select_objects'@'localhost';
grant execute on procedure `list_status_of_jobs` to 'qmanager'@'%';


create definer = 'select_objects'@'localhost'
  procedure list_queued_jobs()
    comment 'List all jobs that should be in the queue'
    reads sql data sql security definer
  begin
    select bin_to_uuid(jobs.id, 1) as job_id, users.auth0_id as user_id
      from jobs join users on jobs.user_id = users.id
     where jobs.status = 'queued';
  end;

grant execute on procedure `list_queued_jobs` to 'select_objects'@'localhost';
grant execute on procedure `list_queued_jobs` to 'qmanager'@'%';


create definer = 'insert_objects'@'localhost'
  procedure add_failure_message (newbinid binary(16), jobbinid binary(16),
                                 message JSON)
    modifies sql data sql security definer
  begin
    insert into job_results (id, job_id, schema_path, type, format, data)
    values (newbinid, jobbinid, '/', 'error message', 'application/json', message);
  end;

grant execute on procedure `add_failure_message` to 'insert_objects'@'localhost';
grant execute on procedure `add_failure_message` to 'update_objects'@'localhost';

create definer = 'update_objects'@'localhost'
  procedure report_job_failure (jobid char(36), message JSON)
    comment 'Mark a job as failed and add a result with an error message'
    modifies sql data sql security definer
  begin
    declare newid char(36) default (uuid());
    declare newbinid binary(16) default (uuid_to_bin(newid, 1));
    declare binjobid binary(16) default (uuid_to_bin(jobid, 1));

    call add_failure_message(newbinid, binjobid, message);
    update jobs set status = 'error' where id = binjobid;
    select newid as result_id;
  end;

grant execute on procedure `report_job_failure` to 'update_objects'@'localhost';
grant execute on procedure `report_job_failure` to 'qmanager'@'%';

-- migrate:down
drop procedure `report_job_failure`;
drop procedure `add_failure_message`;
drop procedure `list_queued_jobs`;
drop procedure `list_status_of_jobs`;
drop user 'qmanager'@'%';

-- migrate:up
alter table job_results modify type varchar(64) not null;

drop procedure add_job_result;
create definer = 'insert_objects'@'localhost'
  procedure add_job_result (auth0id varchar(32), jobid char(36),
                            new_schema_path varchar(128), new_type varchar(64),
                            new_format varchar(64), new_result longblob)
    comment 'Add a result for a job'
    modifies sql data sql security definer
  begin
    declare newid char(36) default (uuid());
    declare binid binary(16) default (uuid_to_bin(newid, 1));
    declare binjobid binary(16) default (uuid_to_bin(jobid, 1));
    declare allowed boolean default (check_users_job(auth0id, jobid));
    declare status varchar(32) default (job_status_func(binjobid));

    if allowed then
      if status = 'complete' or status = 'error' then
        signal sqlstate '42000' set message_text = 'Job already complete',
        mysql_errno = 1062;
      else
        insert into job_results (id, job_id, schema_path, type, format, data)
        values (binid, binjobid, new_schema_path, new_type, new_format, new_result);
        select newid as job_result_id;
      end if;
    else
      signal sqlstate '42000' set message_text = 'Job result upload denied',
        mysql_errno = 1142;
    end if;
  end;
grant execute on procedure `add_job_result` to 'insert_objects'@'localhost';
grant execute on procedure `add_job_result` to 'apiuser'@'%';


-- migrate:down
drop procedure add_job_result;
create definer = 'insert_objects'@'localhost'
  procedure add_job_result (auth0id varchar(32), jobid char(36),
                            new_schema_path varchar(128), new_type varchar(32),
                            new_format varchar(64), new_result longblob)
    comment 'Add a result for a job'
    modifies sql data sql security definer
  begin
    declare newid char(36) default (uuid());
    declare binid binary(16) default (uuid_to_bin(newid, 1));
    declare binjobid binary(16) default (uuid_to_bin(jobid, 1));
    declare allowed boolean default (check_users_job(auth0id, jobid));
    declare status varchar(32) default (job_status_func(binjobid));

    if allowed then
      if status = 'complete' or status = 'error' then
        signal sqlstate '42000' set message_text = 'Job already complete',
        mysql_errno = 1062;
      else
        insert into job_results (id, job_id, schema_path, type, format, data)
        values (binid, binjobid, new_schema_path, new_type, new_format, new_result);
        select newid as job_result_id;
      end if;
    else
      signal sqlstate '42000' set message_text = 'Job result upload denied',
        mysql_errno = 1142;
    end if;
  end;
grant execute on procedure `add_job_result` to 'insert_objects'@'localhost';
grant execute on procedure `add_job_result` to 'apiuser'@'%';

alter table job_results modify type varchar(32) not null;

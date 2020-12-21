-- migrate:up
create table jobs (
  id binary(16) not null default (uuid_to_bin(uuid(), 1)),
  user_id binary(16) not null,
  system_id binary(16) not null,
  definition JSON not null,
  status enum('created', 'queued', 'complete', 'error') default 'created',
  created_at timestamp not null default current_timestamp,
  modified_at timestamp not null default current_timestamp on update current_timestamp,
  primary key (id),
  key jobs_user_id_key (user_id),
  foreign key (user_id)
  references users(id)
  on delete cascade on update restrict
) engine=innodb row_format=compressed;

create table job_data (
  id binary(16) not null default (uuid_to_bin(uuid(), 1)),
  job_id binary(16) not null,
  schema_path varchar(128) not null,
  type varchar(32) not null,
  present boolean not null default false,
  format varchar(64),
  -- query this to check instead of data which may need to fetch from disk
  filename varchar(128),
  -- store data in table for now, future iterations may store data in an object
  -- store like S3 and instead link to it here
  data longblob,
  created_at timestamp not null default current_timestamp,
  modified_at timestamp not null default current_timestamp on update current_timestamp,
  primary key (id),
  key job_data_id_key (job_id),
  foreign key (job_id)
  references jobs(id)
  on delete cascade on update restrict
) engine=innodb row_format=dynamic;


create definer = 'select_objects'@'localhost'
  function check_users_job (auth0id varchar(32), jobid char(36))
    returns boolean
    comment 'Check if a job exists and belongs to the user'
    reads sql data sql security definer
  begin
    return exists(select 1 from jobs where id = uuid_to_bin(jobid, 1)
                                       and user_id = get_user_binid(auth0id));
  end;

grant select on jobs to 'select_objects'@'localhost';
grant execute on function `check_users_job` to 'select_objects'@'localhost';

-- get the computed status of a job
create definer = 'select_objects'@'localhost'
  function job_status_func (jobid binary(16))
    returns varchar(32)
    comment 'Get the status of a job'
    reads sql data sql security definer
  begin
    declare status varchar(32);
    declare allnamed boolean;
    set status = (select jobs.status from jobs where id = jobid);

    if status = 'created' then
      set allnamed = (
        select bit_and(present) from job_data where job_id = jobid
      ) = 1;
      if allnamed then
        return 'prepared';
      else
        return 'incomplete';
      end if;
    end if;
    return status;
  end;

grant execute on function `job_status_func` to 'select_objects'@'localhost';
grant select on job_data to 'select_objects'@'localhost';


create definer = 'select_objects'@'localhost'
  function job_status_transition (jobid binary(16))
    returns timestamp
    comment 'Get the last transition time of the status'
    reads sql data sql security definer
  begin
    declare status varchar(32);
    set status = (select jobs.status from jobs where id = jobid);

    if status = 'created' then
      return ifnull(
        (select max(modified_at) from job_data where job_id = jobid),
        (select created_at from jobs where id = jobid)
      );
    else
      return (select modified_at from jobs where id = jobid);
    end if;
  end;
grant execute on function `job_status_transition` to 'select_objects'@'localhost';


create definer = 'select_objects'@'localhost'
  procedure get_job_status (auth0id varchar(32), jobid char(36))
    comment 'Get status of a job'
    reads sql data sql security definer
  begin
    declare binid binary(16) default (uuid_to_bin(jobid, 1));
    declare allowed boolean default (check_users_job(auth0id, jobid));

    if allowed then
      select job_status_func(binid) as status,
      job_status_transition(binid) as last_change;
    else
      signal sqlstate '42000' set message_text = 'Job status inaccessible',
        mysql_errno = 1142;
    end if;
  end;

grant execute on procedure `get_job_status` to 'select_objects'@'localhost';
grant execute on procedure `get_job_status` to 'apiuser'@'%';


-- get data metadata
create definer = 'select_objects'@'localhost'
  function job_dataobj_func (jobid binary(16))
    returns json
    comment 'Get the data objects as json for the job'
    reads sql data sql security definer
  begin
    return (select json_arrayagg(json_object(
      'id', bin_to_uuid(id, 1), 'schema_path', schema_path, 'type', type, 'filename', filename,
      'data_format', format, 'present', present, 'created_at', created_at, 'modified_at', modified_at)
    ) from job_data where job_id = jobid);
  end;
grant execute on function `job_dataobj_func` to 'select_objects'@'localhost';


-- get job
create definer = 'select_objects'@'localhost'
  procedure get_job (auth0id varchar(32), job_id char(36))
    comment 'Read a jobs metadata'
    reads sql data sql security definer
  begin
    declare binid binary(16) default (uuid_to_bin(job_id, 1));
    declare allowed boolean default (check_users_job(auth0id, job_id));

    if allowed then
      select bin_to_uuid(id, 1) as job_id, bin_to_uuid(user_id, 1) as user_id,
      bin_to_uuid(system_id, 1) as system_id, definition, created_at, modified_at,
      json_object('status', job_status_func(binid), 'last_change', job_status_transition(binid)) as status,
      job_dataobj_func(binid) as data_objects
      from jobs where id = binid;
    else
      signal sqlstate '42000' set message_text = 'Job inaccessible',
        mysql_errno = 1142;
    end if;
  end;

grant execute on procedure `get_job` to 'select_objects'@'localhost';
grant execute on procedure `get_job` to 'apiuser'@'%';


-- list jobs
create definer = 'select_objects'@'localhost'
  procedure list_jobs (auth0id varchar(32))
    comment 'Get metadata for all jobs'
    reads sql data sql security definer
  begin
    select bin_to_uuid(id, 1) as job_id, bin_to_uuid(user_id, 1) as user_id,
           bin_to_uuid(system_id, 1) as system_id, definition, created_at, modified_at,
           json_object('status', job_status_func(id), 'last_change', job_status_transition(id)) as status,
           job_dataobj_func(id) as data_objects
      from jobs where check_users_job(auth0id, bin_to_uuid(id, 1));
  end;

grant execute on procedure `list_jobs` to 'select_objects'@'localhost';
grant execute on procedure `list_jobs` to 'apiuser'@'%';

-- create job incl job data ids
create definer = 'insert_objects'@'localhost'
  procedure create_job (auth0id varchar(32), system_id char(36), definition json,
                        data_items json)
    comment 'Create a new job'
    modifies sql data sql security definer
  begin
    declare sysid binary(16) default (uuid_to_bin(system_id, 1));
    declare jobid char(36) default (uuid());
    declare binid binary(16) default (uuid_to_bin(jobid, 1));
    declare userid binary(16) default (get_user_binid(auth0id));
    declare allowed boolean default (check_users_system(auth0id, system_id));

    if allowed then
      insert into jobs (id, user_id, system_id, definition) values (
        binid, userid, sysid, definition);
      insert into job_data (job_id, schema_path, type)
      select binid, jv.schema_path, jv.type from json_table(data_items, '$[*]' columns (
        schema_path varchar(128) path '$.schema_path' error on empty error on error,
        type varchar(32) path '$.type' error on empty error on error)) as jv;
      select jobid as job_id;
    else
      signal sqlstate '42000' set message_text = 'Job creation denied',
        mysql_errno = 1142;
    end if;
  end;

grant execute on function `check_users_system` to 'insert_objects'@'localhost';
grant execute on procedure `create_job` to 'insert_objects'@'localhost';
grant execute on procedure `create_job` to 'apiuser'@'%';
grant insert on jobs to 'insert_objects'@'localhost';
grant insert on job_data to 'insert_objects'@'localhost';

-- delete job
create definer = 'delete_objects'@'localhost'
  procedure delete_job (auth0id varchar(32), jobid char(36))
    comment 'Delete a job'
    modifies sql data sql security definer
  begin
    declare binid binary(16) default (uuid_to_bin(jobid, 1));
    declare allowed boolean default (check_users_job(auth0id, jobid));

    if allowed then
      delete from jobs where id = binid;
    else
      signal sqlstate '42000' set message_text = 'Job deletion denied',
        mysql_errno = 1142;
    end if;
  end;
grant select(id), delete on jobs to 'delete_objects'@'localhost';
grant execute on function `check_users_job` to 'delete_objects'@'localhost';
grant execute on procedure `delete_job` to 'delete_objects'@'localhost';
grant execute on procedure `delete_job` to 'apiuser'@'%';


create definer = 'select_objects'@'localhost'
  function check_users_job_data (auth0id varchar(32), jobid char(36), dataid char(36))
    returns boolean
    comment 'Check if a job exists and belongs to the user'
    reads sql data sql security definer
  begin
    return exists(
      select 1 from jobs where user_id = get_user_binid(auth0id)
        and id = uuid_to_bin(jobid, 1)
        and id = (select job_id from job_data where id = uuid_to_bin(dataid, 1)));
  end;
grant execute on function `check_users_job_data` to 'select_objects'@'localhost';

-- get job data
create definer = 'select_objects'@'localhost'
  procedure get_job_data (auth0id varchar(32), jobid char(36), dataid char(36))
    comment 'Read the data for a single job data id'
    reads sql data sql security definer
  begin
    declare binid binary(16) default (uuid_to_bin(dataid, 1));
    declare allowed boolean default (check_users_job_data(auth0id, jobid, dataid));

    if allowed then
      select bin_to_uuid(id, 1) as id, bin_to_uuid(job_id, 1) as job_id,
      schema_path, type, filename, data, present, format as data_format, created_at, modified_at
      from job_data where id = binid;
    else
      signal sqlstate '42000' set message_text = 'Job data retrieval denied',
        mysql_errno = 1142;
    end if;
  end;
grant execute on procedure `get_job_data` to 'select_objects'@'localhost';
grant execute on procedure `get_job_data` to 'apiuser'@'%';


-- check if queued
create definer = 'select_objects'@'localhost'
  function check_job_queued (binid binary(16))
    returns boolean
    comment 'Check, from a job data id, if a job is queued or complete'
    reads sql data sql security definer
  begin
    return (select status != 'created' from jobs where id = (
      select job_id from job_data where id = binid));
  end;
grant execute on function `check_job_queued` to 'select_objects'@'localhost';
grant execute on function `check_job_queued` to 'update_objects'@'localhost';

-- add job data
create definer = 'update_objects'@'localhost'
  procedure add_job_data (auth0id varchar(32), jobid char(36), dataid char(36),
                          fname varchar(128), format varchar(64), newdata longblob)
    comment 'Adds data for a job'
    modifies sql data sql security definer
  begin
    declare binid binary(16) default (uuid_to_bin(dataid, 1));
    declare allowed boolean default (check_users_job_data(auth0id, jobid, dataid));
    declare queued boolean default (check_job_queued(binid));

    if allowed then
      if queued then
        signal sqlstate '42000' set message_text = 'Job already queued',
        mysql_errno = 1348;
      else
        update job_data set filename = fname, data = newdata, format = format, present = true where id = binid;
      end if;
    else
      signal sqlstate '42000' set message_text = 'Job data upload denied',
      mysql_errno = 1142;
    end if;
  end;
grant execute on function `check_users_job_data` to 'update_objects'@'localhost';
grant select(id, status), update on jobs to 'update_objects'@'localhost';
grant select(id), update on job_data to 'update_objects'@'localhost';
grant execute on procedure `add_job_data` to 'update_objects'@'localhost';
grant execute on procedure `add_job_data` to 'apiuser'@'%';

-- queue job
create definer = 'update_objects'@'localhost'
  procedure queue_job (auth0id varchar(32), jobid char(36))
    comment 'Change the status to queued if allowed'
    modifies sql data sql security definer
  begin
    declare binid binary(16) default (uuid_to_bin(jobid, 1));
    declare allowed boolean default (check_users_job(auth0id, jobid));
    declare status varchar(32) default (job_status_func(binid));

    if allowed then
      if status = 'prepared' or status = 'queued' then
        update jobs set status = 'queued' where id = binid;
      elseif status = 'incomplete' then
        signal sqlstate '42000' set message_text = 'Missing required job data',
        mysql_errno = 1054;
      else
        signal sqlstate '42000' set message_text = 'Job already computed',
        mysql_errno = 1062;
      end if;
    else
      signal sqlstate '42000' set message_text = 'Job queueing denied',
      mysql_errno = 1142;
    end if;
  end;
grant execute on function `job_status_func` to 'update_objects'@'localhost';
grant execute on function `check_users_job` to 'update_objects'@'localhost';
grant execute on procedure `queue_job` to 'update_objects'@'localhost';
grant execute on procedure `queue_job` to 'apiuser'@'%';

-- migrate:down
drop procedure `queue_job`;
drop procedure `add_job_data`;
drop function `check_job_queued`;
drop procedure `get_job_data`;
drop function `check_users_job_data`;
drop procedure `delete_job`;
drop procedure `create_job`;
drop procedure `list_jobs`;
drop procedure `get_job`;
drop function `job_dataobj_func`;
drop procedure `get_job_status`;
drop function `job_status_transition`;
drop function `job_status_func`;
drop function `check_users_job`;
drop table job_data;
drop table jobs;

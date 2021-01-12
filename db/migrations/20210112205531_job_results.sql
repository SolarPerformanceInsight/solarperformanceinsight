-- migrate:up
create table job_results (
  id binary(16) not null default (uuid_to_bin(uuid(), 1)),
  job_id binary(16) not null,
  schema_path varchar(128) not null,
  type varchar(32) not null,
  format varchar(64) not null,
  data longblob not null,
  created_at timestamp not null default current_timestamp,
  modified_at timestamp not null default current_timestamp on update current_timestamp,
  primary key (id),
  key job_result_id_key (job_id),
  foreign key (job_id)
  references jobs(id)
  on delete cascade on update restrict
) engine=innodb row_format=dynamic;

grant select on job_results to 'select_objects'@'localhost';


-- get result metadata
create definer = 'select_objects'@'localhost'
  procedure get_job_result_metadata (auth0id varchar(32), jobid char(36))
    comment 'Get the metadata for a job result'
    reads sql data sql security definer
  begin
    declare binid binary(16) default (uuid_to_bin(jobid, 1));
    declare allowed boolean default (check_users_job(auth0id, jobid));

    if allowed then
      select bin_to_uuid(id, 1) as id, schema_path, type, format as data_format,
      created_at, modified_at from job_results where job_id = binid;
    else
      signal sqlstate '42000' set message_text = 'Job result metadata retrieval denied',
      mysql_errno=1142;
    end if;
  end;

grant execute on procedure `get_job_result_metadata` to 'select_objects'@'localhost';
grant execute on procedure `get_job_result_metadata` to 'apiuser'@'%';


-- get job result
create definer = 'select_objects'@'localhost'
  function check_users_job_result (auth0id varchar(32), jobid char(36), resultid char(36))
    returns boolean
    comment 'Check if a job result exists and belongs to the user'
    reads sql data sql security definer
  begin
    return exists(
      select 1 from jobs where user_id = get_user_binid(auth0id)
                           and id = uuid_to_bin(jobid, 1)
                           and id = (select job_id from job_results where id = uuid_to_bin(resultid, 1)));
  end;
grant execute on function `check_users_job_result` to 'select_objects'@'localhost';


create definer = 'select_objects'@'localhost'
  procedure get_job_result (auth0id varchar(32), jobid char(36), resultid char(36))
    comment 'Read the data for a single job result id'
    reads sql data sql security definer
  begin
    declare binid binary(16) default (uuid_to_bin(resultid, 1));
    declare allowed boolean default (check_users_job_result(auth0id, jobid, resultid));

    if allowed then
      select bin_to_uuid(id, 1) as id, bin_to_uuid(job_id, 1) as job_id,
      schema_path, type, data, format as data_format, created_at, modified_at
      from job_results where id = binid;
    else
      signal sqlstate '42000' set message_text = 'Job result retrieval denied',
        mysql_errno = 1142;
    end if;
  end;
grant execute on procedure `get_job_result` to 'select_objects'@'localhost';
grant execute on procedure `get_job_result` to 'apiuser'@'%';


-- add job result
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

grant insert on job_results to 'insert_objects'@'localhost';
grant execute on function `check_users_job` to 'insert_objects'@'localhost';
grant execute on function `job_status_func` to 'insert_objects'@'localhost';
grant execute on procedure `add_job_result` to 'insert_objects'@'localhost';
grant execute on procedure `add_job_result` to 'apiuser'@'%';


create definer = 'update_objects'@'localhost'
  procedure set_job_completion (auth0id varchar(32), jobid char(36),
                                newstatus enum('complete', 'error'))
    comment 'Set the job as complete or error'
    modifies sql data sql security definer
  begin
    declare binid binary(16) default (uuid_to_bin(jobid, 1));
    declare allowed boolean default (check_users_job(auth0id, jobid));

    if allowed then
      update jobs set status = newstatus where id = binid;
    else
      signal sqlstate '42000' set message_text = 'Setting job completion denied',
        mysql_errno = 1142;
    end if;
  end;
grant execute on procedure `set_job_completion` to 'update_objects'@'localhost';
grant execute on procedure `set_job_completion` to 'apiuser'@'%';


-- add a completed job with result data
create procedure _add_example_data_3 ()
  modifies sql data
begin
  set @jobid = uuid_to_bin('4910c750-55f1-11eb-a03d-f4939feddd82', 1);
  set @jobdataid = uuid_to_bin('5c22bdd0-55f1-11eb-a03d-f4939feddd82', 1);
  set @userid = uuid_to_bin('17fbf1c6-34bd-11eb-af43-f4939feddd82', 1);
  set @sysid = uuid_to_bin('6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9', 1);
  set @extime = timestamp('2021-01-12 12:37');
  set @uploadtime = timestamp('2021-01-12 12:42');
  set @completetime = timestamp('2021-01-12 13:05');

  set @sysjson = (select cast(definition as json) from systems where id = @sysid);
  set @jobparams = '{"parameters": {
      "system_id": "6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9",
      "time_parameters": {
        "start": "2021-01-11T00:00:00+00:00",
        "end": "2021-01-11T23:59:59+00:00",
        "step": "60:00",
        "timezone": "UTC"
      },
      "weather_granularity": "system",
      "job_type": {
        "calculate": "expected performance"
      },
      "irradiance_type": "standard",
      "temperature_type": "air"}}';
  -- odd annoying way to make sure system def is also json
  set @jobjson = json_set(@jobparams, '$.system_definition', json_value(@sysjson, '$' returning json));

  insert into jobs (id, user_id, system_id, definition, status, created_at, modified_at) values (
    @jobid, @userid, @sysid, @jobjson, 'complete', @extime, @completetime);
  insert into job_data (id, job_id, schema_path, type, present, format, filename,
                        created_at, modified_at, data)
  values (
    @jobdataid, @jobid, '/', 'actual weather data', true,
    'application/vnd.apache.arrow.file', 'weather_data.csv', @extime, @uploadtime,
    from_base64('QVJST1cxAAD/////8AQAABAAAAAAAAoADgAGAAUACAAKAAAAAAEEABAAAAAAAAoADAAAAAQACAAKAAAAYAMAAAQAAAABAAAADAAAAAgADAAEAAgACAAAAAgAAAAQAAAABgAAAHBhbmRhcwAAKwMAAHsiaW5kZXhfY29sdW1ucyI6IFtdLCAiY29sdW1uX2luZGV4ZXMiOiBbXSwgImNvbHVtbnMiOiBbeyJuYW1lIjogInRpbWUiLCAiZmllbGRfbmFtZSI6ICJ0aW1lIiwgInBhbmRhc190eXBlIjogImRhdGV0aW1ldHoiLCAibnVtcHlfdHlwZSI6ICJkYXRldGltZTY0W25zXSIsICJtZXRhZGF0YSI6IHsidGltZXpvbmUiOiAiVVRDIn19LCB7Im5hbWUiOiAiZ2hpIiwgImZpZWxkX25hbWUiOiAiZ2hpIiwgInBhbmRhc190eXBlIjogImludDY0IiwgIm51bXB5X3R5cGUiOiAiaW50NjQiLCAibWV0YWRhdGEiOiBudWxsfSwgeyJuYW1lIjogImRuaSIsICJmaWVsZF9uYW1lIjogImRuaSIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1weV90eXBlIjogImludDY0IiwgIm1ldGFkYXRhIjogbnVsbH0sIHsibmFtZSI6ICJkaGkiLCAiZmllbGRfbmFtZSI6ICJkaGkiLCAicGFuZGFzX3R5cGUiOiAiaW50NjQiLCAibnVtcHlfdHlwZSI6ICJpbnQ2NCIsICJtZXRhZGF0YSI6IG51bGx9LCB7Im5hbWUiOiAidGVtcF9haXIiLCAiZmllbGRfbmFtZSI6ICJ0ZW1wX2FpciIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1weV90eXBlIjogImludDY0IiwgIm1ldGFkYXRhIjogbnVsbH0sIHsibmFtZSI6ICJ3aW5kX3NwZWVkIiwgImZpZWxkX25hbWUiOiAid2luZF9zcGVlZCIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1weV90eXBlIjogImludDY0IiwgIm1ldGFkYXRhIjogbnVsbH1dLCAiY3JlYXRvciI6IHsibGlicmFyeSI6ICJweWFycm93IiwgInZlcnNpb24iOiAiMi4wLjAifSwgInBh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dHlwZSI6ICJpbnQ2NCIsICJtZXRhZGF0YSI6IG51bGx9LCB7Im5hbWUiOiAidGVtcF9haXIiLCAiZmllbGRfbmFtZSI6ICJ0ZW1wX2FpciIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1weV90eXBlIjogImludDY0IiwgIm1ldGFkYXRhIjogbnVsbH0sIHsibmFtZSI6ICJ3aW5kX3NwZWVkIiwgImZpZWxkX25hbWUiOiAid2luZF9zcGVlZCIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1weV90eXBlIjogImludDY0IiwgIm1ldGFkYXRhIjogbnVsbH1dLCAiY3JlYXRvciI6IHsibGlicmFyeSI6ICJweWFycm93IiwgInZlcnNpb24iOiAiMi4wLjAifSwgInBhbmRhc192ZXJzaW9uIjogIjEuMS40In0ABgAAABwBAADUAAAApAAAAHQAAAA8AAAABAAAAAz///8AAAECEAAAABwAAAAEAAAAAAAAAAoAAAB3aW5kX3NwZWVkAABI////AAAAAUAAAABA////AAABAhAAAAAcAAAABAAAAAAAAAAIAAAAdGVtcF9haXIAAAAAfP///wAAAAFAAAAAdP///wAAAQIQAAAAFAAAAAQAAAAAAAAAAwAAAGRoaQCo////AAAAAUAAAACg////AAABAhAAAAAUAAAABAAAAAAAAAADAAAAZG5pANT///8AAAABQAAAAMz///8AAAECEAAAABwAAAAEAAAAAAAAAAMAAABnaGkACAAMAAgABwAIAAAAAAAAAUAAAAAQABQACAAGAAcADAAAABAAEAAAAAAAAQoQAAAAIAAAAAQAAAAAAAAABAAAAHRpbWUAAAAACAAMAAYACAAIAAAAAAADAAQAAAADAAAAVVRDABgFAABBUlJPVzE='));

  set @jobresult0 = uuid_to_bin('d84bdf30-55f2-11eb-a03d-f4939feddd82', 1);
  set @jobresult1 = uuid_to_bin('e525466a-55f2-11eb-a03d-f4939feddd82', 1);
  set @jobresult2 = uuid_to_bin('e566a59c-55f2-11eb-a03d-f4939feddd82', 1);

  insert into job_results (id, job_id, schema_path, type, format,
                           created_at, modified_at, data)
  values (
    @jobresult0, @jobid, '/inverters/0/arrays/0', 'weather data',
    'application/vnd.apache.arrow.file', @completetime, @completetime,
    from_base64('QVJST1cxAAD/////QAMAABAAAAAAAAoADgAGAAUACAAKAAAAAAEEABAAAAAAAAoADAAAAAQACAAKAAAAPAIAAAQAAAABAAAADAAAAAgADAAEAAgACAAAAAgAAAAQAAAABgAAAHBhbmRhcwAABgIAAHsiaW5kZXhfY29sdW1ucyI6IFtdLCAiY29sdW1uX2luZGV4ZXMiOiBbXSwgImNvbHVtbnMiOiBbeyJuYW1lIjogInRpbWUiLCAiZmllbGRfbmFtZSI6ICJ0aW1lIiwgInBhbmRhc190eXBlIjogImRhdGV0aW1ldHoiLCAibnVtcHlfdHlwZSI6ICJkYXRldGltZTY0W25zXSIsICJtZXRhZGF0YSI6IHsidGltZXpvbmUiOiAiVVRDIn19LCB7Im5hbWUiOiAicG9hX2dsb2JhbCIsICJmaWVsZF9uYW1lIjogInBvYV9nbG9iYWwiLCAicGFuZGFzX3R5cGUiOiAiaW50NjQiLCAibnVtcHlfdHlwZSI6ICJpbnQ2NCIsICJtZXRhZGF0YSI6IG51bGx9LCB7Im5hbWUiOiAiY2VsbF90ZW1wZXJhdHVyZSIsICJmaWVsZF9uYW1lIjogImNlbGxfdGVtcGVyYXR1cmUiLCAicGFuZGFzX3R5cGUiOiAiaW50NjQiLCAibnVtcHlfdHlwZSI6ICJpbnQ2NCIsICJtZXRhZGF0YSI6IG51bGx9XSwgImNyZWF0b3IiOiB7ImxpYnJhcnkiOiAicHlhcnJvdyIsICJ2ZXJzaW9uIjogIjIuMC4wIn0sICJwYW5kYXNfdmVyc2lvbiI6ICIxLjEuNCJ9AAADAAAAlAAAAEQAAAAEAAAAiP///wAAAQIQAAAAJAAAAAQAAAAAAAAAEAAAAGNlbGxfdGVtcGVyYXR1cmUAAAAAzP///wAAAAFAAAAAxP///wAAAQIQAAAAJAAAAAQAAAAAAAAACgAAAHBvYV9nbG9iYWwAAAgADAAIAAcACAAAAAAAAAFAAAAAEAAUAAgABgAHAAwAAAAQABAAAAAAAAEKEAAAACAAAAAEAAAAAAAAAAQAAAB0aW1lAAAAAAgADAAGAAgACAAAAAAAAwAEAAAAAwAAAFVUQwD/////+AAAABQAAAAAAAAADAAYAAYABQAIAAwADAAAAAADBAAcAAAAIAEAAAAAAAAAAAAADAAcABAABAAIAAwADAAAAIgAAAAcAAAAFAAAABgAAAAAAAAAAAAAAAQABAAEAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMsAAAAAAAAA0AAAAAAAAAAAAAAAAAAAANAAAAAAAAAAJwAAAAAAAAD4AAAAAAAAAAAAAAAAAAAA+AAAAAAAAAAmAAAAAAAAAAAAAAADAAAAGAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAEIk0YYECCtAAAAPA3AABDlNa1WBYAoPvEHLlYFgBAtPVivFgWAOBsJqm/WBYAgCVX78JYFgAg3oc1xlgWAMCWuHvJWBYAYE/pwcxYFgAACBoI0EAAQMBKTtNAAEB5e5TWQABAMaza2UAAQOrcIN1AAECjDWfgQABAWz6t40AAQBRv8+ZAAEDNnznqQABAhdB/7UAAQD4BxvBAAED2MQz0QABAr2JS90AAQGiTmPpAAOAgxN79WBYAYNn0JAFZFgAAAAAAAAAAAMAAAAAAAAAABCJNGGBAghAAAAAx6AMAAQAPCACgUAAAAAAAAAAAAADAAAAAAAAAAAQiTRhgQIIPAAAAIhkAAQAPCACgUAAAAAAAAAAAAAAA/////wAAAAAQAAAADAAUAAYACAAMABAADAAAAAAABABAAAAAKAAAAAQAAAABAAAAUAMAAAAAAAAAAQAAAAAAACABAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAwAAAAEAAgACgAAADwCAAAEAAAAAQAAAAwAAAAIAAwABAAIAAgAAAAIAAAAEAAAAAYAAABwYW5kYXMAAAYCAAB7ImluZGV4X2NvbHVtbnMiOiBbXSwgImNvbHVtbl9pbmRleGVzIjogW10sICJjb2x1bW5zIjogW3sibmFtZSI6ICJ0aW1lIiwgImZpZWxkX25hbWUiOiAidGltZSIsICJwYW5kYXNfdHlwZSI6ICJkYXRldGltZXR6IiwgIm51bXB5X3R5cGUiOiAiZGF0ZXRpbWU2NFtuc10iLCAibWV0YWRhdGEiOiB7InRpbWV6b25lIjogIlVUQyJ9fSwgeyJuYW1lIjogInBvYV9nbG9iYWwiLCAiZmllbGRfbmFtZSI6ICJwb2FfZ2xvYmFsIiwgInBhbmRhc190eXBlIjogImludDY0IiwgIm51bXB5X3R5cGUiOiAiaW50NjQiLCAibWV0YWRhdGEiOiBudWxsfSwgeyJuYW1lIjogImNlbGxfdGVtcGVyYXR1cmUiLCAiZmllbGRfbmFtZSI6ICJjZWxsX3RlbXBlcmF0dXJlIiwgInBhbmRhc190eXBlIjogImludDY0IiwgIm51bXB5X3R5cGUiOiAiaW50NjQiLCAibWV0YWRhdGEiOiBudWxsfV0sICJjcmVhdG9yIjogeyJsaWJyYXJ5IjogInB5YXJyb3ciLCAidmVyc2lvbiI6ICIyLjAuMCJ9LCAicGFuZGFzX3ZlcnNpb24iOiAiMS4xLjQifQAAAwAAAJQAAABEAAAABAAAAIj///8AAAECEAAAACQAAAAEAAAAAAAAABAAAABjZWxsX3RlbXBlcmF0dXJlAAAAAMz///8AAAABQAAAAMT///8AAAECEAAAACQAAAAEAAAAAAAAAAoAAABwb2FfZ2xvYmFsAAAIAAwACAAHAAgAAAAAAAABQAAAABAAFAAIAAYABwAMAAAAEAAQAAAAAAABChAAAAAgAAAABAAAAAAAAAAEAAAAdGltZQAAAAAIAAwABgAIAAgAAAAAAAMABAAAAAMAAABVVEMAcAMAAEFSUk9XMQ==')
  ), (
    @jobresult1, @jobid, '/inverters/0', 'performance data',
    'application/vnd.apache.arrow.file', @completetime, @completetime,
    from_base64('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')
  ), (
    @jobresult2, @jobid, '/', 'performance data',
    'application/vnd.apache.arrow.file', @completetime, @completetime,
    from_base64('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')
  );

end;

drop procedure add_example_data;
create procedure add_example_data ()
  modifies sql data
begin
  CALL _add_example_data_0;
  CALL _add_example_data_1;
  CALL _add_example_data_2;
  CALL _add_example_data_3;
end;

-- migrate:down
drop procedure add_example_data;
create procedure add_example_data ()
  modifies sql data
begin
  CALL _add_example_data_0;
  CALL _add_example_data_1;
  CALL _add_example_data_2;
  CALL _add_example_data_3;
end;
drop procedure _add_example_data_3;
drop procedure `set_job_completion`;
drop procedure `add_job_result`;
drop procedure `get_job_result`;
drop function `check_users_job_result`;
drop procedure `get_job_result_metadata`;
drop table job_results;

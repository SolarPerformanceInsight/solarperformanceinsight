-- migrate:up
alter table job_data modify type varchar(64) not null;

drop procedure create_job;
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
        type varchar(64) path '$.type' error on empty error on error)) as jv;
      select jobid as job_id;
    else
      signal sqlstate '42000' set message_text = 'Job creation denied',
        mysql_errno = 1142;
    end if;
  end;
grant execute on procedure `create_job` to 'insert_objects'@'localhost';
grant execute on procedure `create_job` to 'apiuser'@'%';


create procedure _add_example_data_6 ()
  modifies sql data
begin
  set @jobid0 = uuid_to_bin('3c392360-76c1-11eb-afc5-f4939feddd82', 1);
  set @jobdataid0_0 = uuid_to_bin('3291fb8c-76c3-11eb-afc5-f4939feddd82', 1);
  set @jobdataid0_1 = uuid_to_bin('3be689f0-76c3-11eb-afc5-f4939feddd82', 1);
  set @jobid1 = uuid_to_bin('1ece4f7a-76c2-11eb-afc5-f4939feddd82', 1);
  set @jobdataid1_0 = uuid_to_bin('46451466-76c3-11eb-afc5-f4939feddd82', 1);
  set @jobdataid1_1 = uuid_to_bin('4eb8697c-76c3-11eb-afc5-f4939feddd82', 1);
  set @jobdataid1_2 = uuid_to_bin('fcafef8c-76c3-11eb-afc5-f4939feddd82', 1);
  set @jobdataid1_3 = uuid_to_bin('0d04f5bc-76c4-11eb-afc5-f4939feddd82', 1);
  set @jobid2 = uuid_to_bin('717eb644-76c5-11eb-8fae-f4939feddd82', 1);
  set @jobdataid2_0 = uuid_to_bin('71431620-76c5-11eb-8fae-f4939feddd82', 1);
  set @jobdataid2_1 = uuid_to_bin('7101c33c-76c5-11eb-8fae-f4939feddd82', 1);
  set @jobdataid2_2 = uuid_to_bin('f6c3c628-76c5-11eb-8fae-f4939feddd82', 1);
  set @jobdataid2_3 = uuid_to_bin('f68b4cf8-76c5-11eb-8fae-f4939feddd82', 1);
  set @userid = uuid_to_bin('17fbf1c6-34bd-11eb-af43-f4939feddd82', 1);
  set @sysid = uuid_to_bin('6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9', 1);
  set @extime = timestamp('2021-02-24 23:58:20');

  set @sysjson = (select cast(definition as json) from systems where id = @sysid);
  set @jobparams0 = '{"parameters": {
      "system_id": "6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9",
      "time_parameters": {
        "start": "2021-01-01T00:00:00+00:00",
        "end": "2021-12-31T23:59:59+00:00",
        "step": "30:00",
        "timezone": "America/Denver"
      },
      "weather_granularity": "system",
      "calculate": "weather-adjusted performance ratio",
      "performance_granularity": "inverter",
      "irradiance_type": "poa",
      "temperature_type": "module"}}';
  set @jobjson0 = json_set(@jobparams0, '$.system_definition', json_value(@sysjson, '$' returning json));
  set @jobparams1 = '{"parameters": {
                    "system_id": "6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9",
                    "time_parameters": {
                    "start": "2021-01-01T00:00:00+00:00",
                    "end": "2021-12-31T23:59:59+00:00",
                    "step": "60:00",
                    "timezone": "America/Denver"
                    },
                    "compare": "predicted and actual performance",
                    "predicted_data_parameters": {
                    "irradiance_type": "standard",
                    "temperature_type": "air",
                    "weather_granularity": "system",
                    "data_available": "weather and AC performance",
                    "performance_granularity": "system"
                    },
                    "actual_data_parameters": {
                    "irradiance_type": "poa",
                    "temperature_type": "module",
                    "weather_granularity": "inverter",
                    "performance_granularity": "inverter"
                    }}}';
  set @jobjson1 = json_set(@jobparams1, '$.system_definition', json_value(@sysjson, '$' returning json));
  set @jobparams2 = '{"parameters": {
                    "system_id": "6b61d9ac-2e89-11eb-be2a-4dc7a6bcd0d9",
                    "compare": "monthly predicted and actual performance"}}';
  set @jobjson2 = json_set(@jobparams2, '$.system_definition', json_value(@sysjson, '$' returning json));

  insert into jobs (id, user_id, system_id, definition, status, created_at, modified_at) values (
    @jobid0, @userid, @sysid, @jobjson0, 'created', @extime, @extime
  ), (
    @jobid1, @userid, @sysid, @jobjson1, 'created', @extime, @extime
  ), (
    @jobid2, @userid, @sysid, @jobjson2, 'created', @extime, @extime
  );

  insert into job_data (id, job_id, schema_path, type, created_at, modified_at) values (
    @jobdataid0_0, @jobid0, '/', 'actual weather data', @extime, @extime
  ), (
    @jobdataid0_1, @jobid0, '/inverters/0', 'actual performance data', @extime, @extime
  ), (
    @jobdataid1_0, @jobid1, '/', 'original weather data', @extime, @extime
  ), (
    @jobdataid1_1, @jobid1, '/', 'predicted performance data', @extime, @extime
  ), (
    @jobdataid1_2, @jobid1, '/inverters/0', 'actual weather data', @extime, @extime
  ), (
    @jobdataid1_3, @jobid1, '/inverters/0', 'actual performance data', @extime, @extime
  ), (
    @jobdataid2_0, @jobid2, '/', 'original monthly weather data', @extime, @extime
  ), (
    @jobdataid2_1, @jobid2, '/', 'predicted monthly performance data', @extime, @extime
  ), (
    @jobdataid2_2, @jobid2, '/', 'actual monthly weather data', @extime, @extime
  ), (
    @jobdataid2_3, @jobid2, '/', 'actual monthly performance data', @extime, @extime
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
  CALL _add_example_data_4;
  CALL _add_example_data_5;
  CALL _add_example_data_6;
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
  CALL _add_example_data_4;
  CALL _add_example_data_5;
end;
drop procedure _add_example_data_6;

drop procedure create_job;
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
grant execute on procedure `create_job` to 'insert_objects'@'localhost';
grant execute on procedure `create_job` to 'apiuser'@'%';

alter table job_data modify type varchar(32) not null;

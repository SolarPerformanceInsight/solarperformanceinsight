-- migrate:up
create procedure _add_example_data_5 ()
  modifies sql data
begin
  -- from _add_example_data_1
  set @extime = timestamp('2020-12-11 19:52');
  set @jobid = uuid_to_bin('e1772e64-43ac-11eb-92c2-f4939feddd82', 1);
  set @otherjobid = uuid_to_bin('7f13ab34-43ad-11eb-80a2-f4939feddd82', 1);
  update jobs set definition = json_set(
    json_remove(definition, '$.parameters.job_type'),
    '$.parameters.compare', 'expected and actual performance',
    '$.parameters.performance_granularity', 'inverter'
  ), modified_at = @extime
   where id in (@jobid, @otherjobid);

  set @jobdataid0 = uuid_to_bin('ecaa5a40-43ac-11eb-a75d-f4939feddd82', 1);
  update job_data set type = 'actual weather data', modified_at = @extime
   where id = @jobdataid0;

  -- completed job in _add_example_data_3
  update jobs set definition = json_set(
    json_remove(definition, '$.parameters.job_type'),
    '$.parameters.calculate', 'expected performance')
   where id = uuid_to_bin('4910c750-55f1-11eb-a03d-f4939feddd82', 1);
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
end;
drop procedure _add_example_data_5;

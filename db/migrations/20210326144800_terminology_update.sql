-- migrate:up
create procedure _add_example_data_7 ()
  modifies sql data
begin
  -- update calculate jobs
  update jobs set definition = json_set(
    definition,
    '$.parameters.calculate', 'reference performance')
  where JSON_EXTRACT(definition, "$.parameters.calculate") = "predicted performance";

  update jobs set definition = json_set(
    definition,
    '$.parameters.calculate', 'modeled performance')
  where JSON_EXTRACT(definition, "$.parameters.calculate") = "expected performance";
  
  -- update compare jobs
  update jobs set definition = json_set(
    definition,
    '$.parameters.compare', 'reference and actual performance')
  where JSON_EXTRACT(definition, "$.parameters.compare") = "predicted and actual performance";

    update jobs set definition = json_set(
    definition,
    '$.parameters.compare', 'monthly reference and actual performance')
  where JSON_EXTRACT(definition, "$.parameters.compare") = "monthly predicted and actual performance";

  update jobs set definition = json_set(
    definition,
    '$.parameters.compare', 'modeled and actual performance')
  where JSON_EXTRACT(definition, "$.parameters.compare") = "expected and actual performance";

  update jobs set definition = JSON_INSERT(
    JSON_REMOVE(definition, '$.parameters.predicted_data_parameters'),
    '$.parameters.reference_data_parameters',
    JSON_EXTRACT(definition, '$.parameters.predicted_data_parameters')
  )
  where JSON_EXTRACT(definition, '$.parameters.predicted_data_parameters') IS NOT NULL;

  update job_data set type = 'reference performance data' where type = 'predicted performance data';
  update job_data set type = 'reference DC performance data' where type = 'predicted DC performance data';
  update job_data set type = 'reference monthly performance data' where type = 'predicted monthly performance data';
  update job_data set type = 'reference monthly weather data' where type = 'original monthly weather data';

  update job_data set type = 'reference weather data' where type = 'original weather data';
  update job_data set type = 'modeled performance data' where type = 'expected performance data';

  -- ensure jobs added in add_example_data 1 and 3 retain their modified_at time
  set @extime = timestamp('2020-12-11 19:52');
  set @jobid = uuid_to_bin('e1772e64-43ac-11eb-92c2-f4939feddd82', 1);
  set @otherjobid = uuid_to_bin('7f13ab34-43ad-11eb-80a2-f4939feddd82', 1);
  update jobs set modified_at = @extime where id in (@jobid, @otherjobid);
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
  CALL _add_example_data_7;
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
  CALL _add_example_data_6;
end;
drop procedure _add_example_data_7;

-- migrate:up
create procedure _add_example_data_4 ()
  modifies sql data
begin
  update jobs set definition = json_merge_patch(
    definition,
    '{"parameters": {"time_parameters": {"start": "2021-01-10T00:00:00+00:00", "end": "2021-01-10T23:59:59+00:00"}}}')
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
drop procedure _add_example_data_4;

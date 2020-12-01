-- migrate:up
create user if not exists
  'apiuser'@'%' identified with caching_sha2_password by
  'terriblepasswordtochange';

create user if not exists
  'insert_objects'@'localhost' identified with caching_sha2_password as
  '$A$005$THISISACOMBINATIONOFINVALIDSALTANDPASSWORDTHATMUSTNEVERBRBEUSED'
  ACCOUNT LOCK;

create user if not exists
  'delete_objects'@'localhost' identified with caching_sha2_password as
  '$A$005$THISISACOMBINATIONOFINVALIDSALTANDPASSWORDTHATMUSTNEVERBRBEUSED'
  ACCOUNT LOCK;

create user if not exists
  'select_objects'@'localhost' identified with caching_sha2_password as
  '$A$005$THISISACOMBINATIONOFINVALIDSALTANDPASSWORDTHATMUSTNEVERBRBEUSED'
  ACCOUNT LOCK;

create user if not exists
  'update_objects'@'localhost' identified with caching_sha2_password as
  '$A$005$THISISACOMBINATIONOFINVALIDSALTANDPASSWORDTHATMUSTNEVERBRBEUSED'
  ACCOUNT LOCK;


-- migrate:down
drop user 'update_objects'@'localhost';
drop user 'select_objects'@'localhost';
drop user 'delete_objects'@'localhost';
drop user 'insert_objects'@'localhost';
drop user 'apiuser'@'%';

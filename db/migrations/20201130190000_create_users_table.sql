-- migrate:up
create table users (
  id binary(16) not null default (uuid_to_bin(uuid(), 1)),
  auth0_id varchar(32) not null,
  created_at timestamp not null default current_timestamp,
  primary key user_id_key (id),
  unique key auth0_id_key (auth0_id)
) engine=innodb row_format=compressed;


create definer = 'select_objects'@'localhost'
  function does_user_exist(auth0id varchar(32))
    returns boolean
    comment 'Check if a user exists or not'
    reads sql data sql security definer
    begin
      return exists(select 1 from users where auth0_id = auth0id);
    end;

grant select on users to 'select_objects'@'localhost';
grant execute on function `does_user_exist` to 'select_objects'@'localhost';

create definer = 'select_objects'@'localhost'
  function get_user_id(auth0id varchar(32))
    returns char(36)
    comment 'Get the id of a user'
    reads sql data sql security definer
  begin
    return (select bin_to_uuid(id, 1) from users where auth0_id = auth0id);
  end;

grant execute on function `get_user_id` to 'select_objects'@'localhost';


create definer = 'select_objects'@'localhost'
  function get_user_binid(auth0id varchar(32))
    returns binary(16)
    comment 'Get the binary id of a user'
    reads sql data sql security definer
  begin
    return (select id from users where auth0_id = auth0id);
  end;

grant execute on function `get_user_binid` to 'select_objects'@'localhost';

-- create user
create definer = 'insert_objects'@'localhost'
  procedure create_user_if_not_exists (in auth0id varchar(32))
    comment 'Creates a user if nonexistent and returns the user id'
    modifies sql data sql security definer
  begin
    declare userid binary(16);
    if not does_user_exist(auth0id) then
      set userid = uuid_to_bin(uuid(), 1);
      insert into users (id, auth0_id) values (userid, auth0id);
      select bin_to_uuid(userid, 1) as user_id;
    else
      select get_user_id(auth0id) as user_id;
    end if;
  end;


grant execute on function `does_user_exist` to 'insert_objects'@'localhost';
grant execute on function `get_user_id` to 'insert_objects'@'localhost';
grant insert on users to 'insert_objects'@'localhost';
grant execute on procedure `create_user_if_not_exists` to 'insert_objects'@'localhost';
grant execute on procedure `create_user_if_not_exists` to 'apiuser'@'%';

-- delete user
create definer = 'delete_objects'@'localhost'
  procedure delete_user_by_auth0id (in auth0id varchar(32))
    comment 'Delete a user by auth0 ID'
    modifies sql data sql security definer
  begin
    declare userid binary(16);
    if does_user_exist(auth0id) then
      delete from users where auth0_id = auth0id;
    else
      signal sqlstate '42000' set message_text = 'User does not exist',
        mysql_errno = 1142;
    end if;
  end;

grant select(auth0_id), delete on users to 'delete_objects'@'localhost';
grant execute on function `does_user_exist` to 'delete_objects'@'localhost';
grant execute on procedure `delete_user_by_auth0id` to 'delete_objects'@'localhost';

-- get user
create definer = 'select_objects'@'localhost'
  procedure get_user (in auth0id varchar(32))
    comment 'Get a user by auth0 id'
    reads sql data sql security definer
  begin
    if does_user_exist(auth0id) then
      select bin_to_uuid(id, 1) as user_id, auth0_id, created_at from users where auth0_id = auth0id;
    else
      signal sqlstate '42000' set message_text = 'User does not exist',
        mysql_errno = 1142;
    end if;
  end;

grant execute on procedure `get_user` to 'select_objects'@'localhost';
grant execute on procedure `get_user` to 'apiuser'@'%';


-- migrate:down
drop procedure get_user;
drop procedure delete_user_by_auth0id;
drop procedure create_user_if_not_exists;
drop function get_user_binid;
drop function get_user_id;
drop function does_user_exist;
drop table users;

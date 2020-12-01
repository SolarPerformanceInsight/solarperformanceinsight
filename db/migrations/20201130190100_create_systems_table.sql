-- migrate:up
create table systems (
  id binary(16) not null default (uuid_to_bin(uuid(), 1)),
  user_id binary(16) not null,
  name varchar(128) not null,
  definition JSON not null,
  created_at timestamp not null default current_timestamp,
  modified_at timestamp not null default current_timestamp on update current_timestamp,
  primary key (id),
  unique system_user_name_key (user_id, name),
  key systems_user_id_key (user_id),
  foreign key (user_id)
    references users(id)
    on delete cascade on update restrict
) engine=innodb row_format=compressed;


create definer = 'select_objects'@'localhost'
  function check_users_system (auth0id varchar(32), systemid char(36))
    returns boolean
    comment 'Check if the system exists and belongs to user'
    reads sql data sql security definer
  begin
    return exists(select 1 from systems where id = uuid_to_bin(systemid, 1)
                                          and user_id = get_user_binid(auth0id));
  end;

grant execute on function `check_users_system` to 'select_objects'@'localhost';

-- get system
create definer = 'select_objects'@'localhost'
  procedure get_system (auth0id varchar(32), systemid char(36))
    comment 'Get the definition for a system'
    reads sql data sql security definer
  begin
    declare binid binary(16) default (uuid_to_bin(systemid, 1));
    declare allowed boolean default (check_users_system(auth0id, systemid));

    if allowed then
      select bin_to_uuid(id, 1) as system_id, bin_to_uuid(user_id, 1) as user_id,
      name, definition, created_at, modified_at from systems where id = binid;
    else
      signal sqlstate '42000' set message_text = 'System inaccessible',
        mysql_errno = 1142;
    end if;
  end;

grant select on systems to 'select_objects'@'localhost';
grant execute on procedure `get_system` to 'select_objects'@'localhost';
grant execute on procedure `get_system` to 'apiuser'@'%';

-- list systems
create definer = 'select_objects'@'localhost'
  procedure list_systems (auth0id varchar(32))
    comment 'List all user systems'
    reads sql data sql security definer
  begin
    select bin_to_uuid(id, 1) as system_id, bin_to_uuid(user_id, 1) as user_id,
           name, definition, created_at, modified_at from systems
     where user_id = get_user_binid(auth0id);
  end;

grant execute on procedure `list_systems` to 'select_objects'@'localhost';
grant execute on procedure `list_systems` to 'apiuser'@'%';

-- create system
create definer = 'insert_objects'@'localhost'
  procedure create_system (auth0id varchar(32), name varchar(128), system_def JSON)
    comment 'Create a new system'
    modifies sql data sql security definer
  begin
    declare sysid char(36) default (uuid());
    declare binid binary(16) default (uuid_to_bin(sysid, 1));
    insert into systems (id, user_id, name, definition) values (
      binid, get_user_binid(auth0id), name, system_def);
    select sysid as system_id;
  end;

grant insert on systems to 'insert_objects'@'localhost';
grant execute on function `get_user_binid` to 'insert_objects'@'localhost';
grant execute on procedure `create_system` to 'insert_objects'@'localhost';
grant execute on procedure `create_system` to 'apiuser'@'%';


-- update system
create definer = 'update_objects'@'localhost'
  procedure update_system (auth0id varchar(32), systemid char(36), system_def JSON)
    comment 'Update a system definition'
    modifies sql data sql security definer
  begin
    declare binid binary(16) default (uuid_to_bin(systemid, 1));
    declare allowed boolean default (check_users_system(auth0id, systemid));
    declare uid binary(16) default get_user_binid(auth0id);

    if allowed then
      update systems set definition = system_def where id = binid;
    else
      signal sqlstate '42000' set message_text = 'Updating system not allowed',
        mysql_errno = 1142;
    end if;
  end;

grant select(id), update on systems to 'update_objects'@'localhost';
grant execute on function `check_users_system` to 'update_objects'@'localhost';
grant execute on function `get_user_binid` to 'update_objects'@'localhost';
grant execute on procedure `update_system` to 'update_objects'@'localhost';
grant execute on procedure `update_system` to 'apiuser'@'%';

-- delete system
create definer = 'delete_objects'@'localhost'
  procedure delete_system (auth0id varchar(32), systemid char(36))
    comment 'Delete a system'
    modifies sql data sql security definer
  begin
    declare binid binary(16) default (uuid_to_bin(systemid, 1));
    declare allowed boolean default (check_users_system(auth0id, systemid));
    declare uid binary(16) default get_user_binid(auth0id);

    if allowed then
      delete from systems where id = binid;
    else
      signal sqlstate '42000' set message_text = 'Deleting system not allowed',
        mysql_errno = 1142;
    end if;
  end;

grant select(id), delete on systems to 'delete_objects'@'localhost';
grant execute on function `check_users_system` to 'delete_objects'@'localhost';
grant execute on function `get_user_binid` to 'delete_objects'@'localhost';
grant execute on procedure `delete_system` to 'delete_objects'@'localhost';
grant execute on procedure `delete_system` to 'apiuser'@'%';

-- migrate:down
drop procedure delete_system;
drop procedure update_system;
drop procedure create_system;
drop procedure list_systems;
drop procedure get_system;
drop function check_users_system;
drop table systems;

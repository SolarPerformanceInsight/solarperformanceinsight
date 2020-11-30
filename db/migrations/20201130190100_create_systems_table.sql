-- migrate:up
create table systems (
  id binary(16) not null default (uuid_to_bin(uuid(), 1)),
  user_id binary(16) not null,
  definition JSON not null,
  created_at timestamp not null default current_timestamp,
  modified_at timestamp not null default current_timestamp on update current_timestamp,
  primary key (id),
  key systems_user_id_key (user_id),
  foreign key (user_id)
    references users(id)
    on delete cascade on update restrict
) engine=innodb row_format=compressed;


-- get system
-- list systems
-- create system
-- update system
-- delete system

-- migrate:down
drop table systems;

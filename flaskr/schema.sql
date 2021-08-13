DROP TABLE IF EXISTS user;
drop table if exists printorder;
DROP TABLE IF EXISTS admn;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS itemorder;

create table admn (
    id integer primary key autoincrement,
    admin_name text unique not null,
    admin_password text not null
);

INSERT INTO admn (admin_name, admin_password) VALUES ('admin_sgsits', '~admin$01');

create table user (
    id integer primary key autoincrement,
    username text unique not null,
    firstname text not null,
    lastname text not null,
    mobileno integer not null,
    emailid text,
    password text not null
);


create table printorder (
    id integer primary key autoincrement,
    printorder_id integer not null,
    created timestamp not null default current_timestamp,
    f_name text not null,
    file_path text not null,
    file_cost integer not null,
    confirmation_received boolean not null, 
    confirmation_admin text default "Pending",
    foreign key (printorder_id) references user (id)
);

create table inventory (
    id integer primary key autoincrement,
    item_name text unique not null,
    item_cost integer not null,
    item_quantity integer default 1
);

create table itemorder(
    id integer primary key autoincrement,
    order_id integer not null,
    item_name text not null,
    order_cost integer default 0,
    item_quantity integer default 1,
    order_created timestamp not null default current_timestamp,
    foreign key (order_id) references user (id)
);



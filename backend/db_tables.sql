/*
создаем таблицы для базы данных, пусть бд называется bankster ))
*/

use bankster;
create table users (
id int primary key auto_increment, 
email varchar(50),
fullname varchar(50),
role_ varchar(15),
is_active bool
);

create table accounts (
id int primary key auto_increment,
balance int,
user_id int,
foreign key(user_id) references users(id)
);

create table payment (
id int primary key auto_increment,
pay int,
account_id int,
foreign key(account_id) references accounts(id)
);

/* 31.10.2026 */
/* в процессе теста нашел косяк с созданием пользователя - нужно поля email и fullname сделать уникальными*/
alter table users add unique(fullname);
alter table users add unique(email);
/* drop table accounts, payment, users; */

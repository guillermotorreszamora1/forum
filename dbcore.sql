drop table if exists post;
drop table if exists thread;
drop table if exists category;
drop table if exists users;
drop type if exists user_type;
CREATE TYPE user_type AS ENUM('User','Moderator','Administrator','Master');
CREATE TABLE category(
	category_id serial primary key,
	n_posts integer default 0,
	n_threads integer default 0,
	name varchar
);
CREATE TABLE thread(
	thread_id serial primary key,
	name varchar,
	category_id int,
	n_posts integer default 0,
	max_pos integer default 0,
	CONSTRAINT category_id_thread_fk FOREIGN KEY (category_id) REFERENCES category(category_id)
);
CREATE TABLE users(
	name varchar unique,
	email varchar,
	sha512pass varchar,
	ip varchar,
	user_id serial primary key,
	type user_type default 'User'
);

CREATE TABLE post(
	post_id serial primary key,
	pos int,
	text varchar,
	user_id int,
	thread_id int,
	post_time timestamp default now(),
	CONSTRAINT user_id_post_fk FOREIGN KEY ( user_id) REFERENCES users(user_id),
	CONSTRAINT thread_id_post_fk FOREIGN KEY (thread_id) REFERENCES thread(thread_id)
);

CREATE INDEX ON post(thread_id);
CREATE INDEX ON thread(category_id);
CREATE INDEX ON post(thread_id,pos);
create index on post(user_id);

-- Function: public.new_post()

-- DROP FUNCTION public.new_post();

CREATE OR REPLACE FUNCTION new_post()
  RETURNS trigger AS $$
BEGIN
UPDATE thread set n_posts=n_posts+1,max_pos=max_pos+1 where NEW.thread_id=thread_id;
UPDATE category set n_posts=n_posts+1 where category_id in (select category_id from thread where NEW.thread_id=thread_id);
NEW.pos := (select max_pos from thread where NEW.thread_id=thread_id);
RETURN NEW;
END;
$$LANGUAGE plpgsql;


CREATE TRIGGER t_new_post
  BEFORE INSERT
  ON post
  FOR EACH ROW
  EXECUTE PROCEDURE new_post();

CREATE OR REPLACE FUNCTION remove_post()
  RETURNS trigger AS $$
BEGIN
UPDATE thread set n_posts=n_posts-1 where OLD.thread_id=thread_id;
UPDATE category set n_posts=n_posts-1 where category_id in (select category_id from thread where OLD.thread_id=thread_id);
RETURN OLD;
END;
$$LANGUAGE plpgsql;

CREATE TRIGGER t_remove_post
  BEFORE DELETE
  ON post
  FOR EACH ROW
  EXECUTE PROCEDURE remove_post();

CREATE OR REPLACE FUNCTION new_thread()
  RETURNS trigger AS $$
BEGIN
UPDATE category set n_threads=n_threads+1 where NEW.category_id=category_id;
RETURN NEW;
END;
$$LANGUAGE plpgsql;

CREATE TRIGGER t_new_thread
  BEFORE INSERT
  ON thread
  FOR EACH ROW
  EXECUTE PROCEDURE new_thread();

CREATE OR REPLACE FUNCTION remove_thread()
  RETURNS trigger AS $$
BEGIN
UPDATE category set n_threads=n_threads-1 where OLD.category_id=category_id;
RETURN OLD;
END;
$$LANGUAGE plpgsql;

CREATE TRIGGER t_remove_thread
  BEFORE DELETE
  ON thread
  FOR EACH ROW
  EXECUTE PROCEDURE remove_thread();

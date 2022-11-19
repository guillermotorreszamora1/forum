insert into users(name) select *  from generate_series(1,100000);
insert into category(name) select *  from generate_series(1,100);
insert into thread(name,category_id) select a.n,floor(random()*100)+1 from generate_series(1,10000) as a(n);
insert into post(text,thread_id,user_id) select a.n,floor(random()*10000)+1,floor(random()*100)+1 from generate_series(1,100000) as a(n);
--delete from post;
--delete from thread where thread_id>0;
select * from thread;
select * from post;
select * from category;

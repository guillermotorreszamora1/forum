
select category.name,count(post.post_id) 
	from category 
	left outer join thread on category.category_id=thread.category_id 
	left outer join post on thread.thread_id=post.thread_id 
	group by category.category_id order by name offset 0 limit 3;
/*select category.name,count(thread.name) 
	from category 
	left outer join thread on category.category_id=thread.category_id 
	group by category.category_id order by name offset 0 limit 3;*/

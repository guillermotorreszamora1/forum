import os
from hashlib import sha512
import random
from sqlalchemy import create_engine,text
import time
DATABASE_URI="postgresql://user:password@localhost/forum"
db_engine = create_engine(DATABASE_URI, echo=False)
def register(user,password,email,ip):
	hashed_password = sha512(password.encode('utf-8')).hexdigest()
	db_engine.execute(text("INSERT INTO users(name,sha512pass,email,ip) values(:name,:password,:email,:ip);"),\
	{"name":user,"password":hashed_password,"email":email,"ip":ip})
def login(user,password):
	hashed_password = sha512(password.encode('utf-8')).hexdigest()
	try:
		results = db_engine.execute(text("SELECT sha512pass,user_id,type FROM users where name=:name"),{"name":user})
		for result in results:
			if result[0]==hashed_password:
				return result[1],result[2]
	except:
		return -1,-1
	return -1,-1
def n_categories():
	results = db_engine.execute(text("SELECT count(*) FROM category"));
	for result in results:
		return result[0]
def generate_random_post():
	for i in range(0,30):
		db_engine.execute(text("INSERT INTO category(name) values (:name)"),{"name":i})
	for i in range(0,300):
		j = random.randint(1,30);
		db_engine.execute(text("INSERT INTO thread(name,category_id) values (:name,:category_id)"),\
			{"name":i,"category_id":j})
	for i in range(0,3000):
		db_engine.execute(text("INSERT INTO post(text,thread_id) values (:text,:thread_id)"),\
			{"text":i,"thread_id":random.randint(1,300)})
def categories_data(inicial,tamano):
	results = db_engine.execute(text("SELECT name,n_posts,n_threads,category_id from category order by name offset :inicial limit :tamano"),\
		{"inicial":inicial,"tamano":tamano})
	formated_results = []
	for result in results:
		dict = {"name":result[0],"n_posts":result[1],"n_threads":result[2],"id":result[3]}
		formated_results.append(dict)
	return formated_results
def n_threads(category):
	try:
		results = db_engine.execute(text("SELECT n_threads from category where category_id=:category_id"),\
		{"category_id":category})
		for result in results:
			return result[0]
	except:
		return -1;
def category_name(category):
	results = db_engine.execute(text("SELECT name from category where category_id=:category_id"),\
		{"category_id":category})
	for result in results:
		return result[0]
def category_data(category,inicial,tamano):
	#start = time.time()
	results = db_engine.execute(text("select name,n_posts,max(post.post_time),thread.thread_id"+\
	" from post,thread where thread.thread_id=post.thread_id and  category_id=:category_id"+\
	" group by(thread.thread_id) order by(max(post.post_time)) desc offset :inicial limit :tamano;"),{"category_id":category,"inicial":inicial,"tamano":tamano})
	#print(time.time()-start)
	formated_results = []
	for result in results:
		dict = {"name":result[0],"n_posts":result[1],"last_post":result[2],"thread_id":result[3]}
		formated_results.append(dict)
	return formated_results
def thread_name(thread):
	try:
		results = db_engine.execute(text("select name from thread where thread_id=:thread_id"),\
			{"thread_id":thread})
		for result in results:
			return result[0]
	except:
		return None
def n_posts(thread):
	try:
		results = db_engine.execute(text("SELECT n_posts from thread where thread_id=:thread_id"),{"thread_id":thread})
		for result in results:
			return result[0]
	except:
		return -1
def thread_data(thread,inicial,tamano):
	results = db_engine.execute(text("select users.name,users.user_id,extract(year from post_time)"+\
		",extract(month from post_time),extract(day from post_time),"+\
		"extract(hour from post_time),extract(minute from post_time),text,post_id "+\
		"from post inner join users on users.user_id=post.user_id where "+\
		"thread_id=:thread_id order by pos offset :inicial limit :tamano"),\
		{"thread_id":thread,"inicial":inicial,"tamano":tamano})
	formated_results = []
	for result in results:
		inicial += 1
		post_time = {"year":int(result[2]),"month":int(result[3]),"day":int(result[4]),
			"hour":int(result[5]),"minute":int(result[6])}
		dict = {"user_name":result[0],"user_id":result[1],"pos":inicial,"post_time":post_time,"text":result[7],"post_id":result[8]}
		formated_results.append(dict)
	return formated_results
def new_post(user_text,user_id,thread_id):
	results = db_engine.execute(text("insert into post(text,user_id,thread_id) values(:text,:user_id,:thread_id)"),\
		{"text":user_text,"user_id":user_id,"thread_id":thread_id})
def new_thread(name,category_id):
	results = db_engine.execute(text("INSERT INTO thread(name,category_id)"+\
	" values(:name,:category_id) RETURNING thread_id"),{"name":name,"category_id":category_id})
	for result in results:
		return result[0]
def get_user_data(user_id):
	results = db_engine.execute(text("select users.type, count(post.post_id),name from users "+\
	"left outer join post on users.user_id=post.user_id where users.user_id=:user_id"+\
	" group by users.user_id;"),{"user_id":user_id})
	for result in results:
		return {"user_type":result[0],"n_posts":result[1],"user_name":result[2]}
	return None
def change_rol(user_id,rol):
	results = db_engine.execute(text("UPDATE users set type =:rol where user_id=:user_id"),\
	{"rol":rol,"user_id":user_id})
def delete_post(post_id):
	results = db_engine.execute(text("delete from post where post_id=:post_id"),{"post_id":post_id});
def delete_thread(thread_id):
	db_engine.execute(text("delete from post where thread_id=:thread_id"),{"thread_id":thread_id})
	db_engine.execute(text("delete from thread where thread_id=:thread_id"),{"thread_id":thread_id})

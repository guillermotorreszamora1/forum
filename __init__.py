from flask import Flask
from flask import jsonify,request,render_template,send_file,redirect,session,abort
import math
import web_base.database
from flask_wtf.csrf import CSRFProtect
posts_per_page=3
app = Flask(__name__,template_folder='templates')
app.secret_key = '81248730c22adb840052359c42ede7a8'
csrf = CSRFProtect(app)
csrf.init_app(app)
def get_acess_level():
    try:
        user_type=session['rol']
        if user_type=='User':
            return 1
        if user_type=='Moderator':
            return 2
        if user_type=='Administrator':
            return 3
        if user_type=='Master':
            return 4
    except:
        pass
    return 0
URL_PREFIX ='/forum'
@app.route(URL_PREFIX,strict_slashes=False)
@app.route(URL_PREFIX+'/',strict_slashes=False)
def main():
    return render_template('index.html',url_prefix=URL_PREFIX,user=check_logged(),user_id=get_user_id())
@app.route(URL_PREFIX+'/main.css')
def css():
    return send_file('templates/main.css',)
@app.route(URL_PREFIX+'/login')
def login_page():
    return render_template('login.html',url_prefix=URL_PREFIX,user=check_logged(),user_id=get_user_id())
@app.route(URL_PREFIX+'/login_call',methods=["POST"])
def login():
    #try:
        id,rol =  database.login(request.form['user'],request.form['password'])
        if id!=None and id!=-1:
            session['user']=request.form['user']
            session['user_id']=id
            session['rol']=rol
        return redirect(URL_PREFIX)
    #except:
        return redirect(URL_PREFIX+'/login')
@app.route(URL_PREFIX+'/logout')
def logout():
    session.clear()
    return redirect(URL_PREFIX)
def check_logged():
    if session and 'user' in session:
        return session['user']
    else:
        return None
def get_user_id():
    if session and 'user_id' in session:
        return session['user_id']
    else:
        return None
@app.route(URL_PREFIX+'/register_call',methods=["POST"])
def register():
    try:
        if request.form['password']==request.form['password2']:
                database.register(request.form['user'],request.form['password'],
                    request.form['email'],request.headers.getlist("X-Forwarded-For")[0])
        return redirect(URL_PREFIX)
    except:
        return redirect(URL_PREFIX)
@app.route(URL_PREFIX+'/categories')
@app.route(URL_PREFIX+'/categories/')
@app.route(URL_PREFIX+'/categories/<int:page>')
def list_categories(page=1):
    categories_per_page=3
    n_categories=database.n_categories()
    max_page=math.ceil(n_categories/categories_per_page)
    first_cat=(page-1)*categories_per_page+1
    last_cat = min((page)*categories_per_page,n_categories)
    if page>max_page or page<1:
        abort(404)
    return render_template('categorias.html',url_prefix=URL_PREFIX,\
    user=check_logged(),n_categories=n_categories,\
        first_cat=first_cat,last_cat=last_cat,page=page,max_page=max_page,\
        categories=database.categories_data(first_cat-1,categories_per_page),user_id=get_user_id())
@app.route(URL_PREFIX+'/category/<int:category>',strict_slashes=False)
@app.route(URL_PREFIX+'/category/<int:category>/',strict_slashes=False)
@app.route(URL_PREFIX+'/category/<int:category>/<int:page>',strict_slashes=False)
@app.route(URL_PREFIX+'/category/<int:category>/<int:page>/',strict_slashes=False)
def list_threads(category,page=1):
    threads_per_page=3
    n_threads=database.n_threads(category)
    if n_threads==-1:
        abort(404)
    category_name =database.category_name(category)
    max_page=math.ceil(n_threads/threads_per_page)
    first_thread=(page-1)*threads_per_page+1
    last_thread=min((page)*threads_per_page,n_threads)
    if page>max_page or page<1:
        abort(404)
    return render_template('category.html',url_prefix=URL_PREFIX,category=category,\
        first_thread=first_thread,last_thread=last_thread,n_threads=n_threads,page=page,\
        max_page=max_page,category_name=category_name,user=check_logged(),\
        threads=database.category_data(category,first_thread-1,threads_per_page),user_id=get_user_id())
@app.route(URL_PREFIX+'/thread/<int:thread>',strict_slashes=False)
@app.route(URL_PREFIX+'/thread/<int:thread>/',strict_slashes=False)
@app.route(URL_PREFIX+'/thread/<int:thread>/<int:page>',strict_slashes=False)
@app.route(URL_PREFIX+'/thread/<int:thread>/<int:page>/',strict_slashes=False)
def list_post(thread,page=1):
    n_posts=database.n_posts(thread)
    if n_posts==-1:
        abort(404)
    max_page=math.ceil(n_posts/posts_per_page)
    first_post=(page-1)*posts_per_page+1
    last_post=min(page*posts_per_page,n_posts)
    max_page = max(1,max_page)
    if page>max_page or page<1:
        abort(404)
    thread_prop = {}
    thread_prop['thread_name']=database.thread_name(thread)
    thread_prop['n_posts']=n_posts
    thread_prop['first_post']=first_post
    thread_prop['last_post']=last_post
    thread_prop['thread_id']=thread
    thread_prop['page']=page
    thread_prop['max_page']=max_page
    acess_level=0
    if 'user' in session:
        acess_level = get_acess_level()
    return render_template('thread.html',url_prefix=URL_PREFIX,user=check_logged(),
    thread_prop=thread_prop,posts=database.thread_data(thread,first_post-1,posts_per_page)\
    ,user_id=get_user_id(),acess_level=acess_level)
@app.route(URL_PREFIX+'/new_post/<int:thread>/')
def new_post(thread):
    thread_name = database.thread_name(thread)
    if thread_name==None:
        abort(404)
    return render_template('new_post.html',url_prefix=URL_PREFIX,\
    thread_name=thread_name,thread_id=thread,user=check_logged(),user_id=get_user_id())
@app.route(URL_PREFIX+'/new_post_call',methods=["POST"])
def new_post_call():
    if not("user" in session):
        abort(401)
    try:
        if database.n_posts(request.form["thread"])==-1 or request.form["text"]==None:
            abort(400)
    except:
        abort(400)
    database.new_post(request.form["text"],session['user_id'],request.form['thread'])
    return redirect(URL_PREFIX+'/thread/'+request.form['thread'])
@app.route(URL_PREFIX+'/new_thread/<int:category>')
def new_thread(category):
    category_name= database.category_name(category)
    if category_name==None:
        abort(404)
    return render_template('new_thread.html',url_prefix=URL_PREFIX,\
    category_name=category_name,category=category,user=check_logged(),user_id=get_user_id())
@app.route(URL_PREFIX+'/new_thread_call',methods=["POST"])
def new_thread_call():
    if not ("user" in session):
        abort(401)
    try:
            if database.n_threads(request.form["category"])==-1 :
                abort(400)
            if request.form['thread_title']=='' or request.form['thread_title']==None:
                abort(400)
            if request.form['text']=='' or request.form['text']==None:
                abort(400)
    except:
        abort(400)
    thread_id = database.new_thread(request.form['thread_title'],request.form["category"])
    database.new_post(request.form["text"],session['user_id'],thread_id)
    return redirect(URL_PREFIX+'/thread/'+str(thread_id))
@app.route(URL_PREFIX+'/About')
def about():
    return render_template('About.html',url_prefix=URL_PREFIX,user=check_logged(),user_id=get_user_id())
@app.route(URL_PREFIX+'/user/<int:user>')
def user_page(user):
    user_data = database.get_user_data(user)
    if user_data!=None:
        return render_template('user.html',url_prefix=URL_PREFIX,\
        user=check_logged(),user_type=user_data['user_type'],n_posts=user_data['n_posts'],\
        user_name=user_data['user_name'],rol=session['rol'],user_id=user)
    else:
        abort(404)
@app.route(URL_PREFIX+'/change_rol',methods=["POST"])
def change_rol():
    if not "user" in session:
        abort(401)
    if session['rol']!='Master':
        abort(403)
    database.change_rol(request.form['user_id'],request.form['rol'])
    return redirect(URL_PREFIX+'/user/'+request.form['user_id'])
@app.route(URL_PREFIX+'/delete_post',methods=["POST"])
def delete_post():
    if not "user" in session:
        abort(401)
    if get_acess_level()<2:
        abort(403)
    database.delete_post(request.form['post_id'])
    max_page = math.ceil(int(request.form['n_posts'])/posts_per_page)
    page = min(int(request.form['page']),max_page)
    return redirect(URL_PREFIX+'/thread/'+request.form['thread_id']+'/'+str(page))
@app.route(URL_PREFIX+'/delete_thread',methods=["POST"])
def delete_thread():
    if not "user" in session:
        abort(401)
    if get_acess_level()<3:
        abort(403)
    database.delete_thread(request.form['thread'])
    return redirect(URL_PREFIX+'/category/'+request.form['category'])

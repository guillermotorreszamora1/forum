To install the forum you should create a database and execute db_core.sql and add a few categories.
Also you should configure nginx as reserve proxy and reserve an address  and a port to this website. After that modify
DATABASE_URI in database.py to connect with the database and URL_PREFIX in __init__.py to match the address configured in nginx.
After that use gunicorn as a WSGI server to execute the code(gunicorn --bind 0.0.0.0:PORT forum:app)

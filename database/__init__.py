from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import psycopg2
#database = SQLAlchemy()

DB_HOST = "ec2-99-80-200-225.eu-west-1.compute.amazonaws.com"
DB_NAME = "d8t87nco360qgb"
DB_USER = "tkkjfwcewyiyyy"
DB_PASS = "45ffc56f105bf668e1ecb8e089261e5d827cd1a43b00f069c75cbf2d2101ca99"


conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
cur = conn.cursor()

cur.execute("CREATE TABLE example (id SERIAL PRIMARY KEY, name VARCHAR)")
#cur.execute("INSERT INTO mere (name) VALUES(%s)", ("Hello",))
#cur.execute("SELECT * FROM mere;")
#cur.execute("SELECT * FROM mere;")
print(cur.fetchall())
conn.commit()
cur.close()
conn.close()

"""
def init_table_posts():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("CREATE TABLE donations (id SERIAL PRIMARY KEY, name VARCHAR, title VARCHAR, category VARCHAR, description VARCHAR, location VARCHAR, reserved VARCHAR);")
    cur.execute("CREATE TABLE requests (id SERIAL PRIMARY KEY, name VARCHAR, description VARCHAR, reserved VARCHAR, );")
    conn.commit()
    cur.close()
    conn.close()

# Create database Model

class Postt(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(200), nullable=False)
    date_created = database.Column(database.DateTime, default=datetime.utcnow)

    def repr(self):
        return '<Name %r>' % self.id
"""
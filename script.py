DB_HOST = "ec2-99-80-200-225.eu-west-1.compute.amazonaws.com"
DB_NAME = "d8t87nco360qgb"
DB_USER = "tkkjfwcewyiyyy"
DB_PASS = "45ffc56f105bf668e1ecb8e089261e5d827cd1a43b00f069c75cbf2d2101ca99"


import psycopg2

#from database import database, Postt

#connect to the db
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
#create cursor to communicate with the db through connection
cur = conn.cursor()

cur.execute("CREATE TABLE mere (id SERIAL PRIMARY KEY, name VARCHAR);")
cur.execute("INSERT INTO mere (name) VALUES(%s)", ("Hello",))
cur.execute("SELECT * FROM mere;")
print(cur.fetchall())

conn.commit()

#close the cursor to stop leaking
cur.close()
#close the connection
conn.close()
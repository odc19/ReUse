from flask import Flask, render_template, request
#from flask_sqlalchemy import SQLAlchemy

import psycopg2
#from database import database, Postt

DB_HOST = "ec2-99-80-200-225.eu-west-1.compute.amazonaws.com"
DB_NAME = "d8t87nco360qgb"
DB_USER = "tkkjfwcewyiyyy"
DB_PASS = "45ffc56f105bf668e1ecb8e089261e5d827cd1a43b00f069c75cbf2d2101ca99"



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///EXAMPLE_database.db'

# db = SQLAlchemy(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/blue/<some_text>")
def index_blue(some_text):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    from_text = request.args.get('given_text')
    cur.execute("INSERT INTO dummy (text) VALUES(%s)", (from_text,))
    conn.commit()
    cur.close()
    conn.close()
    return render_template("index_blue.html", given_text=some_text + " " + from_text)


if __name__ == "__main__":
    app.debug = True
    app.run()

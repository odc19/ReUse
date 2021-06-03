from flask import Flask, render_template, request

import psycopg2

DB_HOST = "ec2-99-80-200-225.eu-west-1.compute.amazonaws.com"
DB_NAME = "d8t87nco360qgb"
DB_USER = "tkkjfwcewyiyyy"
DB_PASS = "45ffc56f105bf668e1ecb8e089261e5d827cd1a43b00f069c75cbf2d2101ca99"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///EXAMPLE_database.db'

# db = SQLAlchemy(app)

req_table = "requests"
don_table = "donations"


def init_table_posts():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    conn.commit()
    cur.close()
    conn.close()


def query_word(word, table, col):
    # if table == req_table:
    #     return "SELECT (id, person_id, title, category, description, location, ) FROM " + table + " WHERE " + col + " LIKE '%" + word + "%' ;"
    # else:
        return "SELECT * FROM " + table + " WHERE " + col + " LIKE '%" + word + "%' ;"


@app.route("/")
def index():
    key_word = request.args.get("search_sentence")
    if not key_word:
        key_word = ""
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()

    posts_with_types = []

    cur.execute(query_word(key_word, req_table, "description"))
    posts = cur.fetchall()
    for post in posts:
        posts_with_types.append({"post": post, "type": "request"})

    cur.execute(query_word(key_word, don_table, "description"))
    posts = cur.fetchall()
    for post in posts:
        posts_with_types.append({"post": post, "type": "donation"})

    for post_with_type in posts_with_types:
        print(post_with_type)
        print("\n")

    conn.commit()
    cur.close()
    conn.close()

    return render_template("index.html", posts_with_types=posts_with_types)


@app.route("/abc")
def new_post():
    return render_template("new_post.html", given_text="YAAAY!!! FINALLY")


@app.route("/post_id=<post_id>/post_type=<post_type>")
def view_post(post_id, post_type):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()

    if post_type == "donation":
        table = don_table
        print("DONATION\n")
    else:
        table = req_table
        print("REQUEST\n")
    cur.execute("SELECT * FROM " + table + " WHERE id = " + post_id + ";")
    post = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return render_template("view_post.html", post=post, post_type=post_type)


def get_table_rows(table):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + table + ";")
    rows_nr = 0
    row = cur.fetchone()
    while row is not None:
        rows_nr += 1
        row = cur.fetchone()
    cur.close()
    conn.close()
    return rows_nr


if __name__ == "__main__":
    app.debug = True
    app.run()

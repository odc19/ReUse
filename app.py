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

logged_person_id = 1


def add_examples(cur):
    cur.execute("INSERT INTO donations (name) VALUES(%s)", ("Monica", "I need some CDs with music", "request",
                                                            "Hello! I really need some CDs for my son's birthday, with the music...", "Bucharest", ""))


def init_table_posts():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE donations (id SERIAL PRIMARY KEY, person_id INT, title VARCHAR, category VARCHAR, description VARCHAR, location VARCHAR, reserved VARCHAR);")
    cur.execute("CREATE TABLE requests (id SERIAL PRIMARY KEY, person_id INT, title VARCHAR, description VARCHAR, reserved VARCHAR);")

    conn.commit()
    cur.close()
    conn.close()


def query_word(word, table, col):
    return "SELECT * FROM " + table + " WHERE " + col + " LIKE '%" + word + "%' ;"


@app.route("/")
def index():
    return render_template("index.html")


def connect_to_db():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    return conn, cur


@app.route("/new_request")
def new_request():
    return render_template("new_request.html")


@app.route("/new_donation")
def new_donation():
    return render_template("new_donation.html")


@app.route("/successful_post_<post_type>", methods=['GET', 'POST'])
def successful_post(post_type):
    conn, cur = connect_to_db()

    title = request.args.get('post_title')
    location = request.args.get('post_location')
    description = request.args.get('post_description')
    category = request.args.get('post_category')

    if post_type == "request":
        cur.execute("INSERT INTO requests (person_id, title, description, category, location) VALUES("
                    + str(logged_person_id) + ", '"
                    + title + "', '"
                    + description + "', '"
                    + category + "', '"
                    + location + "')")
    else:
        condition = request.args.get('post_condition')
        condition_description = request.args.get('post_condition_description')

        cur.execute("INSERT INTO donations (person_id, title, description, category, location, condition, "
                    + "condition_description) VALUES("
                    + str(logged_person_id) + ", '"
                    + title + "', '"
                    + description + "', '"
                    + category + "', '"
                    + location + "', '"
                    + condition + "', '"
                    + condition_description + "')")

    conn.commit()
    conn.close()
    cur.close()
    return render_template("successful_post.html", post_type=post_type)


@app.route("/blue/<some_text>")
def index_blue(some_text):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    from_text = request.args.get('given_text')
    # cur.execute("INSERT INTO dummy (text) VALUES(%s)", (from_text,))
    cur.execute(query_word(from_text, don_table, "description"))
    res1 = cur.fetchall()
    res = ""
    for r in res1:
        res += r[2] + " " + r[3]
    cur.execute(query_word(from_text, req_table, "description"))
    res2 = cur.fetchall()

    res += "\n"

    for r in res2:
        res += r[2] + " " + r[3]
   # res = res1 + res2
    conn.commit()
    cur.close()
    conn.close()
    # return render_template("index_blue.html", given_text=some_text + " " + from_text)
    return render_template("index_blue.html", given_text=res)


if __name__ == "__main__":
    app.debug = True
    app.run()

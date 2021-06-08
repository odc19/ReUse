from flask import Flask, render_template, request

import psycopg2

from post import post_donation, post_request

DB_HOST = "ec2-99-80-200-225.eu-west-1.compute.amazonaws.com"
DB_NAME = "d8t87nco360qgb"
DB_USER = "tkkjfwcewyiyyy"
DB_PASS = "45ffc56f105bf668e1ecb8e089261e5d827cd1a43b00f069c75cbf2d2101ca99"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///EXAMPLE_database.db'

# db = SQLAlchemy(app)

req_table = "requests"
don_table = "donations"
req_fields = "id, person_id, title, category, description, location, reserved"
don_fields = "id, person_id, title, category, description, location, reserved, condition, condition_description"

logged_person_id = 1


def init_table_posts():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    conn.commit()
    cur.close()
    conn.close()


def query_word(word, table, col):
    # return "SELECT * FROM " + table + " WHERE " + col + " LIKE '%" + word + "%' ;"
    if table == req_table:
        return "SELECT " + req_fields + " FROM " + table + " WHERE " \
               + col + " LIKE '%" + word + "%' ;"
    else:
        return "SELECT " + don_fields + " FROM " + table + " WHERE " + col + " LIKE '%" + word + "%' ;"


def make_post_class(query_post, post_type):
    post_id = query_post[0]
    person_id = query_post[1]
    title = query_post[2]
    category = query_post[3]
    description = query_post[4]
    location = query_post[5]
    reserved = query_post[6]

    if post_type == "Donation":
        condition = query_post[7]
        condition_description = query_post[8]
        return post_donation(post_id, person_id, title, category, description, location, reserved, condition,
                             condition_description)
    else:
        return post_request(post_id, person_id, title, category, description, location, reserved)


@app.route("/")
def index():
    key_word = request.args.get("search_sentence")
    if not key_word:
        key_word = ""
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()

    posts_with_types = []
    posts_type = request.args.get('posts_type')

    print(posts_type)

    if posts_type == "all" or posts_type == "request":
        cur.execute(query_word(key_word, req_table, "description"))
        posts = cur.fetchall()
        for post in posts:
            post_obj = make_post_class(post, "Request")
            posts_with_types.append({"post": post_obj, "type": "Request"})

    if posts_type == "all" or posts_type == "donation":
        cur.execute(query_word(key_word, don_table, "description"))
        posts = cur.fetchall()
        for post in posts:
            post_obj = make_post_class(post, "Donation")
            posts_with_types.append({"post": post_obj, "type": "Donation"})

    for post_with_type in posts_with_types:
        print(post_with_type)
        print("\n")

    conn.commit()
    cur.close()
    conn.close()

    return render_template("index.html", posts_with_types=posts_with_types)


@app.route("/posts_by_category/", methods=['GET', 'POST'])
def posts_by_category():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()

    category = request.form["category"]
    category2 = request.form.category()
    category3 = request.args.get("category")
    post_with_types = []

    print("category\n")
    #print(category)
    #print(category2)
    #print(category3)
    print("end\n")

    cur.execute(query_word(category, req_table, "category"))
    posts = cur.fetchall()
    for post in posts:
        post_obj = make_post_class(post, "Request")
        post_with_types.append({"post": post_obj, "type": "Request"})

    cur.execute(query_word(category, don_table, "category"))
    posts = cur.fetchall()
    for post in posts:
        post_obj = make_post_class(post, "Donation")
        post_with_types.append({"post": post_obj, "type": "Donation"})

    for post in post_with_types:
        print(post)
        print("\n")

    conn.commit()
    cur.close()
    conn.close()

    return render_template("index.html", posts_with_types=post_with_types)


@app.route("/abc")
def new_post():
    return render_template("new_post.html", given_text="YAAAY!!! FINALLY")


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

    if post_type == "Request":
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


@app.route("/post_id=<post_id>/post_type=<post_type>")
def view_post(post_id, post_type):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()

    if post_type == "Donation":
        table = don_table
        cur.execute("SELECT " + don_fields + " FROM " + table + " WHERE id = " + post_id + ";")
    else:
        table = req_table
        cur.execute("SELECT " + req_fields + " FROM " + table + " WHERE id = " + post_id + ";")
    post = cur.fetchone()
    post_obj = make_post_class(post, post_type)

    if post_type == "Donation":
        cur.execute("SELECT DISTINCT name, email FROM interested_donations "
                    + "INNER JOIN users ON interested_donations.interested_id = users.id "
                    + "AND interested_donations.post_id = " + post_id + ";")
    else:
        cur.execute("SELECT DISTINCT name, email FROM interested_requests "
                    + "INNER JOIN users ON interested_requests.interested_id = users.id "
                    + "AND interested_requests.post_id = " + post_id + ";")
    interested_people = cur.fetchall()

    cur.execute("SELECT name, email FROM users WHERE id = " + str(post_obj.person_id) + ";")
    owner = cur.fetchone()

    print(owner)

    conn.commit()

    cur.close()
    conn.close()

    if post_type == "Donation":
        return render_template("view_donation.html", post=post_obj, owner=owner, interested_people=interested_people)
    else:
        return render_template("view_request.html", post=post_obj, owner=owner, interested_people=interested_people)


@app.route("/pick_new_post")
def pick_new_post():
    return render_template("pick_new_post.html")


@app.route("/<post>")
def view_donation(post):
    return render_template("view_donation.html", post=post)


@app.route("/<post>")
def view_request(post):
    return render_template("view_request.html", post=post)


@app.route("/request_sent/<donation_id>")
def request_sent(donation_id):
    conn, cur = connect_to_db()
    cur.execute("INSERT INTO interested_donations (post_id, interested_id) VALUES ("
                + str(donation_id) + ", "
                + str(logged_person_id) + ")")
    conn.commit()
    cur.close()
    conn.close()
    return index()


@app.route("/donation_sent/<request_id>")
def donation_sent(request_id):
    conn, cur = connect_to_db()
    cur.execute("INSERT INTO interested_requests (post_id, interested_id) VALUES ("
                + str(request_id) + ", "
                + str(logged_person_id) + ")")
    conn.commit()
    cur.close()
    conn.close()
    return index()


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

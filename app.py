from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from flask_hashing import Hashing
import psycopg2
from flask_bcrypt import Bcrypt

from post import post_donation, post_request
from models import User

DB_HOST = "ec2-99-80-200-225.eu-west-1.compute.amazonaws.com"
DB_NAME = "d8t87nco360qgb"
DB_USER = "tkkjfwcewyiyyy"
DB_PASS = "45ffc56f105bf668e1ecb8e089261e5d827cd1a43b00f069c75cbf2d2101ca99"

salt = "@:vkf7s(WO9As8xsEo2_Zsd?fzcZb."

app = Flask(__name__)
# hashing = Hashing(app)
bcrypt = Bcrypt(app)
# hashing.init_app(app)
app.secret_key = 'if!9gYPfde_&)Go'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.get(user_id)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///EXAMPLE_database.db'

# db = SQLAlchemy(app)

req_table = "requests"
don_table = "donations"
req_fields = "id, person_id, title, category, description, location, reserved"
don_fields = "id, person_id, title, category, description, location, reserved, condition, condition_description"


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


def query_2_words(word1, word2, table, col1, col2):
    # return "SELECT * FROM " + table + " WHERE " + col + " LIKE '%" + word + "%' ;"
    if table == req_table:
        return "SELECT " + req_fields + " FROM " + table + " WHERE " \
               + col1 + " LIKE '%" + word1 + "%' AND " + col2 + " LIKE '%" + word2 + "%' ;"
    else:
        return "SELECT " + don_fields + " FROM " + table + " WHERE " \
               + col1 + " LIKE '%" + word1 + "%' AND " + col2 + " LIKE '%" + word2 + "%' ;"


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
    category = request.args.get("category")

    if not posts_type:
        posts_type = "all"

    print(posts_type)
    print(category)

    if posts_type == "all" or posts_type == "request":
        if category:
            cur.execute(query_2_words(key_word, category, req_table, "description", "category"))
        else:
            cur.execute(query_word(key_word, req_table, "description"))
        posts = cur.fetchall()
        for post in posts:
            post_obj = make_post_class(post, "Request")
            posts_with_types.append({"post": post_obj, "type": "Request"})

    if posts_type == "all" or posts_type == "donation":
        if category:
            cur.execute(query_2_words(key_word, category, don_table, "description", "category"))
        else:
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


@app.route("/abc")
def new_post():
    return render_template("new_post.html", given_text="YAAAY!!! FINALLY")


def connect_to_db():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    return conn, cur


@app.route("/new_request")
@login_required
def new_request():
    return render_template("new_request.html")


@app.route("/new_donation")
@login_required
def new_donation():
    return render_template("new_donation.html")


@app.route("/successful_post_<post_type>", methods=['GET', 'POST'])
def successful_post(post_type):
    conn, cur = connect_to_db()

    title = request.args.get('post_title')
    location = request.args.get('post_location')
    description = request.args.get('post_description')
    category = request.args.get('post_category')

    print("\n")
    print(current_user.user_id)
    print("\n")
    print(title)
    print("\n")
    print(description)
    print("\n")
    print(category)
    print("\n")
    print(location)
    print("\n")

    if post_type == "request":
        cur.execute("INSERT INTO requests (person_id, title, description, category, location) VALUES("
                    + str(current_user.user_id) + ", '"
                    + title + "', '"
                    + description + "', '"
                    + category + "', '"
                    + location + "')")
    else:
        condition = request.args.get('post_condition')
        condition_description = request.args.get('post_condition_description')

        cur.execute("INSERT INTO donations (person_id, title, description, category, location, condition, "
                    + "condition_description) VALUES("
                    + str(current_user.user_id) + ", '"
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


@app.route("/view_my_post_<my_post_id>_<my_post_type>")
def view_my_post(my_post_id, my_post_type):
    conn, cur = connect_to_db()
    if my_post_type == "Request":
        cur.execute("SELECT " + req_fields + " FROM " + req_table + " WHERE id = " + my_post_id + ";")
    else:
        cur.execute("SELECT " + don_fields + " FROM " + don_table + " WHERE id = " + my_post_id + ";")

    my_post = cur.fetchone()
    my_post_obj = make_post_class(my_post, my_post_type)

    if my_post_type == "Donation":
        cur.execute("SELECT DISTINCT name, email FROM interested_donations "
                    + "INNER JOIN users ON interested_donations.interested_id = users.id "
                    + "AND interested_donations.post_id = " + my_post_id + ";")
    else:
        cur.execute("SELECT DISTINCT name, email FROM interested_requests "
                    + "INNER JOIN users ON interested_requests.interested_id = users.id "
                    + "AND interested_requests.post_id = " + my_post_id + ";")
    interested_people = cur.fetchall()

    conn.commit()

    cur.close()
    conn.close()

    if my_post_type == "Request":
        return render_template("view_my_request.html", my_post=my_post_obj, interested_people=interested_people)
    else:
        return render_template("view_my_donation.html", my_post=my_post_obj, interested_people=interested_people)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.get_by_email(email)

    if user:
        flash('Email address already exists')
        return redirect(url_for('signup'))

    password.encode('utf-8')
    hashed_password = bcrypt.generate_password_hash(password.encode('utf-8'), salt).decode("utf-8")
    conn, cur = connect_to_db()
    cur.execute("INSERT INTO users (name, password, email) VALUES('"
                + name + "', '"
                + hashed_password + "', '"
                + email + "')")
    conn.commit()
    conn.close()
    cur.close()
    return redirect(url_for('login'))


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.get_by_email(email)

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    password.encode('utf-8')
    if not user or not bcrypt.check_password_hash(user.password, password.encode('utf-8')): # , '@:vkf7s(WO9As8xsEo2_Zsd?fzcZb.'):
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('profile'))


@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, email=current_user.email)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/pick_new_post")
@login_required
def pick_new_post():
    return render_template("pick_new_post.html")


@app.route("/request_sent/<donation_id>")
def request_sent(donation_id):
    conn, cur = connect_to_db()
    cur.execute("INSERT INTO interested_donations (post_id, interested_id) VALUES ("
                + str(donation_id) + ", "
                + str(current_user.user_id) + ")")
    conn.commit()
    cur.close()
    conn.close()
    return index()


@app.route("/donation_sent/<request_id>")
def donation_sent(request_id):
    conn, cur = connect_to_db()
    cur.execute("INSERT INTO interested_requests (post_id, interested_id) VALUES ("
                + str(request_id) + ", "
                + str(current_user.user_id) + ")")
    conn.commit()
    cur.close()
    conn.close()
    return index()


@app.route("/my_donations")
def my_donations():
    conn, cur = connect_to_db()
    cur.execute("SELECT " + don_fields + " FROM " + don_table + " WHERE person_id = " + str(current_user.user_id) + ";")

    my_donations_with_types = []

    donations = cur.fetchall()
    for d in donations:
        my_donation_obj = make_post_class(d, "Donation")
        print(my_donation_obj.description)
        my_donations_with_types.append({"post": my_donation_obj, "type": "Donation"})

    conn.commit()

    cur.close()
    conn.close()

    return render_template("my_donations.html", my_donations_with_types=my_donations_with_types)


@app.route("/my_requests")
def my_requests():
    conn, cur = connect_to_db()
    cur.execute("SELECT " + req_fields + " FROM " + req_table + " WHERE person_id = " + str(current_user.user_id) + ";")

    my_requests_with_types = []

    requests = cur.fetchall()
    for r in requests:
        my_request_obj = make_post_class(r, "Request")
        print(my_request_obj.description)
        my_requests_with_types.append({"post": my_request_obj, "type": "Request"})

    conn.commit()

    cur.close()
    conn.close()

    return render_template("my_requests.html", my_requests_with_types=my_requests_with_types)


@app.route("/my_posts")
def my_posts():
    return render_template("index.html")


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

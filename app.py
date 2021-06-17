from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from haversine import haversine,Unit
from opencage.geocoder import OpenCageGeocode

import psycopg2
from datetime import datetime

from flask_bcrypt import Bcrypt
from datetime import date

from rating import rating_class
from post import post_donation, post_request
from models import User

DB_HOST = "ec2-99-80-200-225.eu-west-1.compute.amazonaws.com"
DB_NAME = "d8t87nco360qgb"
DB_USER = "tkkjfwcewyiyyy"
DB_PASS = "45ffc56f105bf668e1ecb8e089261e5d827cd1a43b00f069c75cbf2d2101ca99"

# salt = "@:vkf7s(WO9As8xsEo2_Zsd?fzcZb."

app = Flask(__name__, template_folder="./templates")
# hashing = Hashing(app)
bcrypt = Bcrypt(app)
geocoder = OpenCageGeocode('432d61b9748c468c9d36f47300a8b0b0')
#GoogleMaps(app, key="AIzaSyCde99Yr7TvjwQe7rqVYloE_4NXNAfemIo")
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
req_fields = "id, person_id, title, category, description, location, reserved, date, charity, lat, lng"
don_fields = "id, person_id, title, category, description, location, reserved, date, charity, lat, lng, condition, condition_description"


def init_table_posts():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    conn.commit()
    cur.close()
    conn.close()


def query_word(word, table, col):
    if table == req_table:
        return "SELECT " + req_fields + " FROM " + table + " WHERE " \
               + col + " LIKE '%" + word + "%' "
    else:
        return "SELECT " + don_fields + " FROM " + table + " WHERE " + col + " LIKE '%" + word + "%' "


def query_2_words(word1, word2, table, col1, col2):
    if table == req_table:
        return "SELECT " + req_fields + " FROM " + table + " WHERE " \
               + col1 + " LIKE '%" + word1 + "%' AND " + col2 + " LIKE '%" + word2 + "%' "
    else:
        return "SELECT " + don_fields + " FROM " + table + " WHERE " \
               + col1 + " LIKE '%" + word1 + "%' AND " + col2 + " LIKE '%" + word2 + "%' "


def get_user_id_from_name(user_name):
    conn, cur = connect_to_db()
    cur.execute("SELECT id FROM users WHERE name = '" + user_name + "';")
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return user_id


def get_pos_neg_rating(message):
    if message == "Trustworthy" or message == "Met on time" or message == "They were kind, polite":
        return "positive"
    elif message == "Other":
        return "neutral"
    return "negative"


def make_post_class(query_post, post_type):
    post_id = query_post[0]
    person_id = query_post[1]
    title = query_post[2]
    category = query_post[3]
    description = query_post[4]
    location = query_post[5]
    reserved = query_post[6]
    date = query_post[7]
    is_charity = query_post[8]
    lat = query_post[9]
    lng = query_post[10]

    if post_type == "Donation":
        condition = query_post[11]
        condition_description = query_post[12]
        return post_donation(post_id, person_id, title, category, description, location, reserved, date, is_charity,
                             condition, condition_description, lat, lng)
    else:
        return post_request(post_id, person_id, title, category, description, location, reserved, date, is_charity, lat, lng)


def in_range(lng_location, lat_location, lat_post, lng_post, location_range):
    try:
        return haversine((lng_location, lat_location), (lng_post, lat_post)) <= int(location_range)
    except:
        return False


def post_timeout(date):
    currentDate = datetime.now()

    dateDatetime = datetime(
                            year=date.year,
                            month=date.month,
                            day=date.day,
                           )

    print(currentDate)
    print(dateDatetime)
    print((currentDate - dateDatetime).days)

    return (currentDate - dateDatetime).days >= 90


@app.route("/")
def index():
    key_word = request.args.get("search_sentence")

    if not key_word:
        key_word = ""

    key_words = key_word.split()

    if len(key_words) > 0:
        first_word = key_words[0]
    else:
        first_word = ""

    posts_with_types = []
    posts_type = request.args.get('posts_type')
    poster = request.args.get('poster')
    see_reserved_posts = request.args.get('reserved_post')
    sort_by = request.args.get('sort_by')
    category = request.args.get("category")
    condition = request.args.get("condition")

    location = request.args.get("location")
    location_range = request.args.get("location_range")
    if location:
        forward = geocoder.geocode(location)
        lng_location = forward[0]['geometry']['lng']
        lat_location = forward[0]['geometry']['lat']
    if not location_range:
        location_range = 4

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()

    print("see_reserved_posts = ", see_reserved_posts)

    if not posts_type:
        posts_type = "all"

    print(posts_type)
    print(category)

    if posts_type == "all" or posts_type == "request":
        if category:
            query = query_2_words(first_word, category, req_table, "description", "category")
        else:
            query = query_word(first_word, req_table, "description")
        if len(key_words) >= 2:
            for i in (1, len(key_words) - 1):
                query += " UNION "
                if category:
                    query += query_2_words(key_words[i], category, req_table, "description", "category")
                else:
                    query += query_word(key_words[i], req_table, "description")
        if current_user.is_authenticated:
            query += "AND person_id != " + str(current_user.user_id)
        if sort_by == "Date":
            query += " ORDER BY date DESC"
        query += ";"
        cur.execute(query)
        posts = cur.fetchall()
        for post in posts:
            post_obj = make_post_class(post, "Request")
            if not post_obj.lat:
                forward = geocoder.geocode(post_obj.location)
                try:
                    post_obj.lng = forward[0]['geometry']['lng']
                    print("REQ HERE")
                    post_obj.lat = forward[0]['geometry']['lat']
                    query = "update requests set lat = " + str(post_obj.lat) + ", lng = " + str(post_obj.lng) + " where id = " + str(post_obj.id) + " ;"
                    print(query)
                    cur.execute(query)
                except:
                    continue
            if not location or in_range(lng_location, lat_location, post_obj.lat, post_obj.lng, location_range):
                if poster == "all" or (post_obj.is_charity == "yes") == (poster == "charities"):
                    if see_reserved_posts == "yes" or not post_obj.reserved:
                        if not post_timeout(post_obj.date):
                            posts_with_types.append({"post": post_obj, "type": "Request"})

    if posts_type == "all" or posts_type == "donation":
        if category:
            query = query_2_words(first_word, category, don_table, "description", "category")
        else:
            query = query_word(first_word, don_table, "description")
        if len(key_words) >= 2:
            for i in (1, len(key_words) - 1):
                query += " UNION "
                if category:
                    query += query_2_words(key_words[i], category, don_table, "description", "category")
                else:
                    query += query_word(key_words[i], don_table, "description")
        if current_user.is_authenticated:
            query += "AND person_id != " + str(current_user.user_id)
        if sort_by == "Date":
            query += " ORDER BY date DESC"
        query += ";"
        cur.execute(query)
        posts = cur.fetchall()
        for post in posts:
            post_obj = make_post_class(post, "Donation")
            print("donation id = " + str(post_obj.id))
            if not post_obj.lat:

                forward = geocoder.geocode(post_obj.location)
                try:
                    post_obj.lng = forward[0]['geometry']['lng']
                    print("DON HERE")
                    post_obj.lat = forward[0]['geometry']['lat']
                    query = "update donations set lat = " + str(post_obj.lat) + ", lng = " + str(post_obj.lng) + " where id = " + str(post_obj.id) + " ;"
                    print(query)
                    cur.execute(query)
                except:
                    print("continue exception for donation id = " + str(post_obj.id))
                    continue
            if not condition or post_obj.condition == condition:
                if not location or in_range(lng_location, lat_location, post_obj.lat, post_obj.lng, location_range):
                    if poster == "all" or (post_obj.is_charity == "yes") == (poster == "charities"):
                        if see_reserved_posts == "yes" or not post_obj.reserved:
                            if not post_timeout(post_obj.date):
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
    return render_template("new_post.html", given_text="YAAAY!!! ")


def get_full_stars_rating(pos_neu_no, neg_no):
    total = pos_neu_no + neg_no
    if total == 0:
        return 0
    ratio = (pos_neu_no / total) * 5
    if ratio < 0.5:
        return 0
    if ratio >= 0.5 and ratio < 1.5:
        return 1
    elif ratio >= 1.5 and ratio < 2.5:
        return 2
    elif ratio >= 2.5 and ratio < 3.5:
        return 3
    elif ratio >= 3.5 and ratio < 4.5:
        return 4
    return 5


def get_negative_rating(ratings):
    neg_no = 0
    all_no = len(ratings)

    for rating in ratings:
        r = rating[3]
        if r == "negative":
            neg_no += 1
    return neg_no


def get_neutral_rating(ratings):
    neu_no = 0
    all_no = len(ratings)

    for rating in ratings:
        r = rating[3]
        if r == "neutral":
            neu_no += 1
    return neu_no


def get_positive_ratings(ratings):
    pos_no = 0
    all_no = len(ratings)

    for rating in ratings:
        r = rating[3]
        if r == "positive":
            pos_no += 1

    return pos_no


@app.route("/post_id/post_type/user_profile_<user>")
def other_user_profile(user):
    rating_list = []
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    query = "select id, rating_type, rating_description, pos_neg_type from ratings where id = " + str(
        get_user_id_from_name(user)) + ";"
    cur.execute(query)
    ratings = cur.fetchall()
    print(ratings)
    for rating in ratings:
        rating_obj = rating_class(rating[0], rating[1], rating[2], rating[3])
        rating_list.append({"rating_obj": rating_obj})
    conn.commit()
    cur.close()
    conn.close()
    pos_no = get_positive_ratings(ratings)
    neu_no = get_neutral_rating(ratings)
    neg_no = get_negative_rating(ratings)
    pos_neu_no = pos_no + neu_no
    all_no = len(ratings)
    full_stars = get_full_stars_rating(pos_neu_no, neg_no)

    fake_full_stars_list = []
    for i in range(0, full_stars):
        fake_full_stars_list.append({"fake_star_obj"})

    fake_empty_stars_list = []
    for i in range(0, 5 - full_stars):
        fake_empty_stars_list.append({"fake_star_obj"})

    rating_message = "This user doesn't have any ratings yet."

    if (not all_no == 0) and pos_neu_no < all_no / 2:
        rating_message = str(neg_no) + "/" + str(all_no) + " negative ratings"
    elif not all_no == 0:
        rating_message = str(pos_no) + "/" + str(all_no) + " positive ratings"
    return render_template("other_user_profile.html", rating_list=rating_list, full_stars=fake_full_stars_list,
                           empty_stars=fake_empty_stars_list, rating_message=rating_message, owner=user)


@app.route("/post_id/post_type/user_profile_<user>/rating")
def user_rating(user):
    return render_template("user_rating.html", owner=user)


@app.route("/post_id/post_type/user_profile_<user>/messages")
def send_message(user):
    return render_template("send_message.html", owner=user)


@app.route("/post_id/post_type/user_profile_<user>/all_ratings")
def see_all_ratings(user):
    rating_list = []
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    query = "select id, rating_type, rating_description, pos_neg_type from ratings where id = " + str(
        get_user_id_from_name(user)) + ";"
    cur.execute(query)
    ratings = cur.fetchall()
    print(ratings)
    for rating in ratings:
        rating_obj = rating_class(rating[0], rating[1], rating[2], rating[3])
        rating_list.append({"rating_obj": rating_obj})
    conn.commit()
    cur.close()
    conn.close()
    return render_template("see_all_ratings.html", rating_list=rating_list, owner=user)


@app.route("/post_id/post_type/user_profile_<user>/report")
def report_user(user):
    return render_template("report_user.html", owner=user)


@app.route("/post_id/post_type/user_profile_<user>/report/finish_report")
def finish_report_action(user):
    message_description = request.args.get("report_description")
    message_type = request.args.get("message")
    user_id = get_user_id_from_name(user)
    print(user_id)
    print(message_type)
    print(message_description)
    conn, cur = connect_to_db()
    cur.execute("INSERT INTO reports (id, message_type, report_description) VALUES("
                + str(user_id) + ", '"
                + message_type + "', '"
                + message_description + "');")
    conn.commit()

    cur.close()
    conn.close()
    return render_template("finish_report_action.html", owner=user, message=message_type,
                           description=message_description)


@app.route("/post_id/post_type/user_profile_<user>/rating/finish_rating")
def finish_rating_action(user):
    message_description = request.args.get("rating_description")
    rating_type = request.args.get("message")
    user_id = get_user_id_from_name(user)
    pos_neg_type = get_pos_neg_rating(rating_type)
    conn, cur = connect_to_db()
    cur.execute("INSERT INTO ratings (id, rating_type, rating_description, pos_neg_type) VALUES("
                + str(user_id) + ", '"
                + rating_type + "', '"
                + message_description + "', '"
                + pos_neg_type + "');")
    conn.commit()

    cur.close()
    conn.close()
    return render_template("finish_rating_action.html", owner=user, message=rating_type,
                           description=message_description)


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
    today = date.today().strftime('%Y-%m-%d')
    forward = geocoder.geocode(location)
    lng = forward[0]['geometry']['lng']
    lat = forward[0]['geometry']['lat']

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
    print(today)
    print("\n")

    if post_type == "request":
        cur.execute("INSERT INTO requests (person_id, title, description, category, location, date, lat, lng) VALUES("
                    + str(current_user.user_id) + ", '"
                    + title + "', '"
                    + description + "', '"
                    + category + "', '"
                    + location + "', '"#CONVERT(datetime, '"
                    + today + "', '"
                    + str(lat) + "', '"
                    + str(lng) + "');")
    else:
        condition = request.args.get('post_condition')
        condition_description = request.args.get('post_condition_description')

        cur.execute("INSERT INTO donations (person_id, title, description, category, location, condition, "
                    + "condition_description, date, lat, lng) VALUES("
                    + str(current_user.user_id) + ", '"
                    + title + "', '"
                    + description + "', '"
                    + category + "', '"
                    + location + "', '"
                    + condition + "', '"
                    + condition_description + "', '"#CONVERT(datetime, '"
                    + today + "', '"
                    + str(lat) + "', '"
                    + str(lng) + "');")

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
        cur.execute("SELECT DISTINCT name, email, id FROM interested_donations "
                    + "INNER JOIN users ON interested_donations.interested_id = users.id "
                    + "AND interested_donations.post_id = " + post_id + ";")
    else:
        cur.execute("SELECT DISTINCT name, email, id FROM interested_requests "
                    + "INNER JOIN users ON interested_requests.interested_id = users.id "
                    + "AND interested_requests.post_id = " + post_id + ";")
    interested_people = cur.fetchall()

    cur.execute("SELECT name, email FROM users WHERE id = " + str(post_obj.person_id) + ";")
    owner = cur.fetchone()
    cur.fetchall()

    query = "SELECT reserved from " + table + " WHERE id = " + post_id + ";"
    cur.execute(query)
    reserved_person = cur.fetchone()[0]
    print(reserved_person)

    conn.commit()

    cur.close()
    conn.close()

    if post_type == "Donation":
        return render_template("view_donation.html", post=post_obj, owner=owner, interested_people=interested_people,
                               reserved_person=reserved_person, lat=post_obj.lat, lng=post_obj.lng)
    else:
        return render_template("view_request.html", post=post_obj, owner=owner, interested_people=interested_people,
                               reserved_person=reserved_person, lat=post_obj.lat, lng=post_obj.lng)


@app.route("/post_id/post_type/<type>/<description>")
def view_rating(type, description):
    return render_template("view_rating.html", type=type, description=description)


@app.route("/view_my_post_<my_post_id>_<my_post_type>")
def view_my_post(my_post_id, my_post_type):
    conn, cur = connect_to_db()
    if my_post_type == "Request":
        table = req_table
        fields = req_fields
    else:
        table = don_table
        fields = don_fields

    cur.execute("SELECT " + fields + " FROM " + table + " WHERE id = " + my_post_id + ";")

    my_post = cur.fetchone()
    my_post_obj = make_post_class(my_post, my_post_type)

    if my_post_type == "Donation":
        cur.execute("SELECT DISTINCT name, email, users.id FROM interested_donations "
                    + "INNER JOIN users ON interested_donations.interested_id = users.id "
                    + "AND interested_donations.post_id = " + my_post_id + ";")
    else:
        cur.execute("SELECT DISTINCT name, email, users.id FROM interested_requests "
                    + "INNER JOIN users ON interested_requests.interested_id = users.id "
                    + "AND interested_requests.post_id = " + my_post_id + ";")
    interested_people = cur.fetchall()
    print(interested_people)

    query = "SELECT reserved from " + table + " WHERE id = " + my_post_id + ";"
    cur.execute(query)
    reserved_person = cur.fetchone()[0]
    print(reserved_person)

    conn.commit()

    cur.close()
    conn.close()

    if my_post_type == "Request":
        return render_template("view_my_request.html", my_post=my_post_obj, interested_people=interested_people,
                               reserved_person=reserved_person, my_post_id=my_post_id, my_post_type=my_post_type)
    else:
        return render_template("view_my_donation.html", my_post=my_post_obj, interested_people=interested_people,
                               reserved_person=reserved_person, my_post_id=my_post_id, my_post_type=my_post_type)


@app.route("/reserved_post/<reserved_person>/my_post_<post_id>_<post_type>")
def reserved_post(reserved_person, post_id, post_type):
    reserved_id = get_user_id_from_name(reserved_person)
    conn, cur = connect_to_db()

    if post_type == "Request":
        cur.execute("UPDATE requests SET reserved = " + str(reserved_id) + " WHERE id = " + post_id + " ;")

    else:
        cur.execute("UPDATE donations SET reserved = " + str(reserved_id) + " WHERE id = " + post_id + " ;")

    conn.commit()

    cur.close()
    conn.close()
    return render_template("reserved_post.html", reserved_person=reserved_person)


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
    hashed_password = bcrypt.generate_password_hash(password.encode('utf-8')).decode("utf-8")
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
    if not user or not bcrypt.check_password_hash(user.password,
                                                  password.encode('utf-8')):  # , '@:vkf7s(WO9As8xsEo2_Zsd?fzcZb.'):
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('index'))


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
@login_required
def request_sent(donation_id):
    conn, cur = connect_to_db()
    cur.execute("INSERT INTO interested_donations (post_id, interested_id) VALUES ("
                + str(donation_id) + ", "
                + str(current_user.user_id) + ")")
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('view_post', post_id=donation_id, post_type="Donation"))


@app.route("/donation_sent/<request_id>")
@login_required
def donation_sent(request_id):
    conn, cur = connect_to_db()
    cur.execute("INSERT INTO interested_requests (post_id, interested_id) VALUES ("
                + str(request_id) + ", "
                + str(current_user.user_id) + ")")
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('view_post', post_id=request_id, post_type="Request"))


@app.route("/my_donations")
def my_donations():
    conn, cur = connect_to_db()
    cur.execute("SELECT " + don_fields + " FROM " + don_table + " WHERE person_id = " + str(current_user.user_id) + ";")

    my_donations_with_types = []
    my_timeouted_donations_with_types = []

    donations = cur.fetchall()
    for d in donations:
        my_donation_obj = make_post_class(d, "Donation")
        print(my_donation_obj.description)
        if post_timeout(my_donation_obj.date):
            my_timeouted_donations_with_types.append({"post": my_donation_obj, "type": "Donation"})
        else:
            my_donations_with_types.append({"post": my_donation_obj, "type": "Donation"})

    conn.commit()

    cur.close()
    conn.close()

    return render_template("my_donations.html", my_donations_with_types=my_donations_with_types,
                           my_timeouted_donations_with_types=my_timeouted_donations_with_types)


@app.route("/my_requests")
def my_requests():
    conn, cur = connect_to_db()
    cur.execute("SELECT " + req_fields + " FROM " + req_table + " WHERE person_id = " + str(current_user.user_id) + ";")

    my_requests_with_types = []
    my_timeouted_requests_with_types = []

    requests = cur.fetchall()
    for r in requests:
        my_request_obj = make_post_class(r, "Request")
        print(my_request_obj.description)
        if post_timeout(my_request_obj.date):
            my_timeouted_requests_with_types.append({"post": my_request_obj, "type": "Request"})
        else:
            my_requests_with_types.append({"post": my_request_obj, "type": "Request"})

    conn.commit()

    cur.close()
    conn.close()

    return render_template("my_requests.html", my_requests_with_types=my_requests_with_types,
                           my_timeouted_requests_with_types=my_timeouted_requests_with_types)


@app.route("/my_posts")
def my_posts():
    return render_template("index.html")


@app.route("/activated_post/<my_post_id>/<my_post_type>")
def activated_post(my_post_id, my_post_type):
    today = date.today().strftime('%Y-%m-%d')

    conn, cur = connect_to_db()

    if my_post_type == "Request":
        table = req_table
        fields = req_fields
    else:
        table = don_table
        fields = don_fields

    cur.execute("SELECT " + fields + " FROM " + table + " WHERE id = " + my_post_id + ";")

    my_post = cur.fetchone()
    my_post_obj = make_post_class(my_post, my_post_type)

    cur.execute("UPDATE " + table + " SET date = '" + today + "' WHERE id = " + my_post_id + ";")

    conn.commit()

    cur.close()
    conn.close()

    return render_template("activated_post.html", post={"post": my_post_obj, "type": my_post_type})


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


@app.route("/post_id/post_type/map/location_<loc>")
def mapview(loc):
    forward = geocoder.geocode(loc)
    lng = forward[0]['geometry']['lng']
    lat = forward[0]['geometry']['lat']
    print(forward[0]['geometry']['lng'])
    return render_template('example.html', lng=lng, lat=lat)


if __name__ == "__main__":
    app.debug = True
    app.run()

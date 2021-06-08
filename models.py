
import psycopg2

DB_HOST = "ec2-99-80-200-225.eu-west-1.compute.amazonaws.com"
DB_NAME = "d8t87nco360qgb"
DB_USER = "tkkjfwcewyiyyy"
DB_PASS = "45ffc56f105bf668e1ecb8e089261e5d827cd1a43b00f069c75cbf2d2101ca99"

#req_fields = "user_id, email, password, name, authenticated"

req_fields = "id, name, email"
table = "users"


class User:

    """def __init__(self, user_id, email, password, name, authenticated):
        self.user_id = user_id
        self.email = email
        self.password = password
        self.name = name
        self.authenticated = authenticated"""

    def __init__(self, id, name, email, rating):
        self.user_id = id
        self.email = email
        self.name = name

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email

    @staticmethod
    def get(user_id):
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cur = conn.cursor()

        cur.execute("SELECT " + req_fields + " FROM " + table + " WHERE email = '" + user_id + "';")

        user = cur.fetchall()[0]

        conn.commit()
        cur.close()
        conn.close()

        """user_id = user[0]
        email = user[1]
        password = user[2]
        name = user[3]
        authenticated = user[4]"""

        user_id = user[0]
        name = user[1]
        email = user[2]
        return User(user_id, name, email, 0)

    @staticmethod
    def get_by_email(email):
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cur = conn.cursor()

        cur.execute("SELECT " + req_fields + " FROM " + table + " WHERE email = '" + email + "';")

        users = cur.fetchall()

        conn.commit()
        cur.close()
        conn.close()

        if len(users) == 0:
            return None

        user = users[0]
        """user_id = user[0]
        email = user[1]
        password = user[2]
        name = user[3]"""
        user_id = user[0]
        name = user[1]
        email = user[2]
        return User(user_id, name, email, 0)

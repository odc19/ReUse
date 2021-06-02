from flask import Flask, render_template, request
from database import cur, conn
#from flask_sqlalchemy import SQLAlchemy


#from database import database, Postt


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///EXAMPLE_database.db'

# db = SQLAlchemy(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/blue/<some_text>")
def index_blue(some_text):
    from_text = request.args.get('given_text')
    cur.execute("INSERT INTO dummy (text) VALUES(%s)", (from_text,))
    conn.commit()
    cur.close()
    conn.close()
    return render_template("index_blue.html", given_text=some_text + " " + from_text)


if __name__ == "__main__":
    app.debug = True
    app.run()

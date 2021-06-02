from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/blue/<some_text>")
def index_blue(some_text):
    form_text = request.args.get('given_text')
    return render_template("index_blue.html", given_text=some_text + " " + form_text)


if __name__ == "__main__":
    app.debug = True
    app.run()
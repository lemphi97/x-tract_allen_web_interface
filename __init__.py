import flask

app = flask.Flask(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'

@app.route("/")
def default():
    return flask.redirect(flask.url_for("home"))

@app.route("/home/")
def home():
    return flask.render_template("index.html", varTest="Test variable")

@app.route("/interface/")
def interface():
    return flask.render_template("interface.html")

@app.route("/experiments/")
def experiments():
    return flask.render_template("allenBrain.html")

@app.route("/aboutWebsite/")
def aboutWebsite():
    return flask.render_template("aboutWebsite.html")

@app.route("/test/")
def test():
    return "Test page text. Can takes HTML inline (<em>HELLO</em>)"

@app.route("/<name>/")
def user(name):
    return f"Hello {name}!"

if __name__ == "__main__":
    app.run(debug=True)
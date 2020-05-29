# Dependencies
import flask
import allensdk_utils as utils

# Init website
app = flask.Flask(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'

@app.route("/")
def default():
    return flask.redirect(flask.url_for("home"))

@app.route("/home/")
def home():
    return flask.render_template("index.html")

@app.route("/interface/")
def interface():
    return flask.render_template("interface.html")

@app.route("/experiments/")
def experiments():
    return flask.render_template (
        "allenBrain.html",
        cre_neg_exp=utils.cre_neg_exp,
        cre_pos_exp=utils.cre_pos_exp,
        struct_dict=utils.st_dict
    )

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
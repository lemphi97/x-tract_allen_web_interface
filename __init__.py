# Dependencies
import flask
import imageio
import pandas as pd
from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache
from allensdk.api.queries.image_download_api import ImageDownloadApi
from allensdk.api.queries.ontologies_api import OntologiesApi

# Init website
app = flask.Flask(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'

# Interactions with allensdk
mcc = MouseConnectivityCache()
st_tree = mcc.get_structure_tree()

all_exp = mcc.get_experiments(dataframe=True)
nb_exp = len(all_exp)

def get_all_id(experiences):
    all_id = []
    # This loop can iterate over all our experiments
    for i in range(0, len(experiences)):
        all_id.append(experiences.iloc[i]['id'])
    return all_id

@app.route("/")
def default():
    return flask.redirect(flask.url_for("home"))

@app.route("/home/")
def home():
    return flask.render_template("index.html")

@app.route("/interface/")
def interface():
    return flask.render_template("interface.html", mcc=mcc)

@app.route("/experiments/")
def experiments():
    return flask.render_template("allenBrain.html", all_exp=all_exp, nb_exp=nb_exp)

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
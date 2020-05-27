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

# Interactions with allensdk (will put in its own file sometime)
# return all id in an array
def get_all_id(experiences):
    all_id = []
    # This loop can iterate over all our experiments
    for i in range(0, len(experiences)):
        all_id.append(experiences.iloc[i]['id'])
    return all_id

# return all structure in a dict (key: id, value: name with acronym)
def get_struct_in_dict(experiences, st_tree):
    st_dict = {}

    for i in range(0, len(experiences)):
        index_val = experiences.iloc[i]
        struct_id = index_val['structure_id']

        if str(struct_id) not in st_dict:
            struct_name = index_val['structure_name']
            struct_acron = index_val['structure_abbrev']
            st_dict[str(struct_id)] = struct_name + " (" + struct_acron + ")"

        struct_p_i_s = index_val['primary_injection_structure']
        if struct_p_i_s != struct_id and str(struct_p_i_s) not in st_dict:
            struct_dict = st_tree.get_structures_by_id([struct_p_i_s])[0]
            st_dict[str(struct_p_i_s)] = struct_dict['name'] + " (" + struct_dict['acronym'] + ")"

    return st_dict

mcc = MouseConnectivityCache()

all_exp = mcc.get_experiments(dataframe=True)
nb_exp = len(all_exp)

st_tree = mcc.get_structure_tree()
st_dict = get_struct_in_dict(all_exp, st_tree)

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
    return flask.render_template("allenBrain.html", all_exp=all_exp)

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
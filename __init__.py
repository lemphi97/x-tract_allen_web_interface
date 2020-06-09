# Dependencies
import flask
#https://github.com/shengulong/flask-compress
from flask_compress import Compress
import allensdk_utils as utils

'''
If one of the var below is true, it means we have the render the template
for the section again when we client ask for it.
'''
home_require_update = True
interface_require_update = True
exp_require_update = True
volume_require_update = True
about_web_require_update = True

# Init website
app = flask.Flask(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'
#app.config['SERVER_NAME'] = 'xtract.com'

# TODO test compression
Compress(app)

@app.route("/")
def default():
    return flask.redirect(flask.url_for("home"))

@app.route("/home/")
def home():
    global home_require_update
    if home_require_update:
        rendered_template = flask.render_template("index.html.j2")
        with open(app.static_folder + "/html/rendered_template/index.html", "w") as f:
            f.write(rendered_template)
        home_require_update = False
        return rendered_template
    else:
        # https://stackoverflow.com/questions/24578330/flask-how-to-serve-static-html
        return flask.current_app.send_static_file('html/rendered_template/index.html')

@app.route("/interface/")
def interface():
    global interface_require_update
    if interface_require_update:
        rendered_template = flask.render_template("interface.html.j2")
        with open(app.static_folder + "/html/rendered_template/interface.html", "w") as f:
            f.write(rendered_template)
        interface_require_update = False
        return rendered_template
    else:
        return flask.current_app.send_static_file('html/rendered_template/interface.html')
    return flask.render_template("interface.html")

@app.route("/experiments/")
def experiments():
    global exp_require_update
    if exp_require_update:
        rendered_template = flask.render_template(
            "allen_brain.html.j2",
            all_exp=utils.all_exp,
            struct_dict=utils.st_dict
        )
        with open(app.static_folder + "/html/rendered_template/allen_brain.html", "w") as f:
            f.write(rendered_template)
        exp_require_update = False
        return rendered_template
    else:
        return flask.current_app.send_static_file('html/rendered_template/allen_brain.html')

@app.route("/experiments/<id>/")
def experiment(id):
    return flask.render_template(
        "experiment.html.j2",
        exp=utils.all_exp.loc[int(id)],
        struct_dict=utils.st_dict
    )

@app.route("/volume_viewer/")
def volume_viewer():
    global volume_require_update
    if volume_require_update:
        rendered_template = flask.render_template("volume_viewer.html.j2")
        with open(app.static_folder + "/html/rendered_template/volume_viewer.html", "w") as f:
            f.write(rendered_template)
        volume_require_update = False
        return rendered_template
    else:
        return flask.current_app.send_static_file('html/rendered_template/volume_viewer.html')

@app.route("/about_website/")
def about_website():
    global about_web_require_update
    if about_web_require_update:
        rendered_template = flask.render_template("about_website.html.j2")
        with open(app.static_folder + "/html/rendered_template/about_website.html", "w") as f:
            f.write(rendered_template)
        about_web_require_update = False
        return rendered_template
    else:
        return flask.current_app.send_static_file('html/rendered_template/about_website.html')

@app.route("/test/")
def test():
    return "Test page text. Can takes HTML inline (<em>HELLO</em>)"

if __name__ == "__main__":
    app.run(debug=True)
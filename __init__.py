# Dependencies
import flask
# flask_socketio recommends eventlet for better performance
from flask_socketio import SocketIO
from flask_socketio import emit
from flask_compress import Compress #https://github.com/shengulong/flask-compress
import allensdk_utils as utils

from shutil import make_archive
import io
import pathlib
import zipfile

# Init website
app = flask.Flask(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'
#app.config["SECRET_KEY"] = "secretencryptionkey"
#app.config['SERVER_NAME'] = 'xtract.com'

socketio = SocketIO(app)

# TODO test compression
Compress(app)

# Global variables
home_require_update = True
interface_require_update = True
exp_require_update = True
volume_require_update = True
about_web_require_update = True
all_exp = utils.get_all_exp()
st_dict = utils.get_struct_in_dict(all_exp)

@socketio.on('req_download', namespace="/request_zip")
def handle_download_request(req_id, req_img, res):
    download_id = flask.request.sid
    tmp_folder = app.static_folder + "/tmp/" + download_id

    # download experiments nrrd
    for exp_id in req_id:
        utils.exp_save_nrrd(exp_id, req_img, res, tmp_folder)

    # make zip
    make_archive(app.static_folder + "/tmp/" + download_id, 'zip', tmp_folder)

    # delete tmp folder
    #todo

    # send zip file
    #flask.current_app.send_static_file("tmp/" + download_id + "zip")
    emit('zip_ready', download_id, broadcast=False)

@app.route('/download-zip/<zip_id>')
def request_zip(zip_id):
    base_path = pathlib.Path('./data/')
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for f_name in base_path.iterdir():
            z.write(f_name)
    data.seek(0)
    return flask.send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='data.zip'
    )
    #https://stackoverflow.com/questions/24612366/delete-an-uploaded-file-after-downloading-it-from-flask

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
            all_exp=all_exp,
            struct_dict=st_dict
        )
        with open(app.static_folder + "/html/rendered_template/allen_brain.html", "w") as f:
            f.write(rendered_template)
        exp_require_update = False
        return rendered_template
    else:
        return flask.current_app.send_static_file('html/rendered_template/allen_brain.html')

@app.route("/experiments/<exp_id>/")
def experiment(exp_id):
    return flask.render_template(
        "experiment.html.j2",
        exp=all_exp.loc[int(exp_id)],
        struct_dict=st_dict
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

if __name__ == "__main__":
    socketio.run(app, debug=True)
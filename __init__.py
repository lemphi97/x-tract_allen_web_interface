from sys import modules
def validate_import(module_name):
    valid = True
    if module_name not in modules:
        print(module_name, 'was not imported')
        valid = False
    return valid

# Framework
import flask

# Socket (flask_socketio recommends eventlet for better performance)
from flask_socketio import SocketIO, emit

# for executing terminal cmd (git)
from subprocess import Popen, PIPE, STDOUT

# Generate secret key
from os import urandom

# For testing files compression
from shutil import make_archive
import io
import pathlib
import zipfile

# Custom files
import allensdk_utils as utils
validate_import('allensdk_utils')
import forms
validate_import('forms')

# Init website
app = flask.Flask(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'
app.config["SECRET_KEY"] = urandom(24).hex()
#app.config['SERVER_NAME'] = 'xtract.com'

socketio = SocketIO(app)

# Global variables
all_exp = utils.get_all_exp()
st_dict = utils.get_struct_in_dict(all_exp)

# Check for globus SDK instead
@socketio.on('req_download', namespace="/request_zip")
def handle_download_request(req_id, req_img, res):
    download_id = flask.request.sid
    tmp_folder = app.static_folder + "/tmp/" + download_id

    # download experiments nrrd #todo wayyy to slow
    for exp_id in req_id:
        utils.exp_save_nrrd(exp_id, req_img, res, tmp_folder)

    # make zip
    make_archive(app.static_folder + "/tmp/" + download_id, 'zip', tmp_folder)

    # delete tmp folder
    #todo

    # send zip file
    #flask.current_app.send_static_file("tmp/" + download_id + "zip")
    emit('zip_ready', download_id, broadcast=False)

@app.before_first_request
def render_templates():
    # get HEAD commit log
    git_cmd = Popen(['git', 'log', '-1'], stdout=PIPE, stderr=STDOUT)
    head_commit, stderr = git_cmd.communicate()
    head_commit = head_commit.decode("utf-8")
    head_commit = head_commit.split('\n')

    # home
    rendered_template = flask.render_template(
        "index.html.j2",
        commit_info=head_commit
    )
    with open(app.static_folder + "/html/rendered_template/index.html", "w") as f:
        f.write(rendered_template)

    # interface
    rendered_template = flask.render_template(
        "interface.html.j2",
        commit_info=head_commit
    )
    with open(app.static_folder + "/html/rendered_template/interface.html", "w") as f:
        f.write(rendered_template)

    # allen_brain
    f_source = forms.form1()
    f_hotspot = forms.form2()
    rendered_template = flask.render_template(
        "allen_brain.html.j2",
        all_exp=all_exp,
        struct_dict=st_dict,
        f_source=f_source,
        f_hotspot=f_hotspot,
        commit_info=head_commit
    )
    with open(app.static_folder + "/html/rendered_template/allen_brain.html", "w") as f:
        f.write(rendered_template)

    # volume_viewer
    rendered_template = flask.render_template(
        "volume_viewer.html.j2",
        commit_info=head_commit
    )
    with open(app.static_folder + "/html/rendered_template/volume_viewer.html", "w") as f:
        f.write(rendered_template)

    # about_website
    rendered_template = flask.render_template(
        "about_website.html.j2",
        commit_info=head_commit
    )
    with open(app.static_folder + "/html/rendered_template/about_website.html", "w") as f:
        f.write(rendered_template)

@app.route('/download-zip/<zip_id>')
def request_zip(zip_id):
    #todo
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
    #https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url

@app.route("/")
def default():
    return flask.redirect(flask.url_for("home"))

@app.route("/home/")
def home():
    # https://stackoverflow.com/questions/24578330/flask-how-to-serve-static-html
    return flask.current_app.send_static_file('html/rendered_template/index.html')

@app.route("/interface/")
def interface():
    return flask.current_app.send_static_file('html/rendered_template/interface.html')

@app.route("/experiments/")
def experiments():
    return flask.current_app.send_static_file('html/rendered_template/allen_brain.html')

@app.route("/experiments/<param>/")
def experiment_search(param):
    if (param.isdigit()):
        exp = all_exp.loc[int(param)]
        struct = st_dict[exp['structure_id']]
        prim_inj_struct = st_dict[exp['primary_injection_structure']]
        sect_id, res, ranges = utils.get_exp_img_sections_info(param)
        return flask.render_template(
            "experiment.html.j2",
            exp=exp,
            struct=struct,
            prim_inj_struct=prim_inj_struct,
            sect_id=sect_id,
            sect_res=res,
            sect_ranges=ranges
        )
    else:
        # For using pre-establish filters specified in the url
        return flask.current_app.send_static_file('html/rendered_template/allen_brain.html')

@app.route("/experiments/forms/correlation/")
def form_correlation():
    f_correlation = forms.f_correlation()
    if f_correlation.validate_on_submit():
        return "Correlation search"
    return "Error with form submit"

@app.route("/experiments/forms/source/", methods=['POST'])
def form_source():
    f_source = forms.form1()
    if f_source.validate_on_submit():
        return "SOURCE: field1: {}, field2: {}".format(f_source.field1.data, f_source.field2.data)
    return "Error with form submit"

@app.route("/experiments/forms/hotspot/", methods=['POST'])
def form_hotspot():
    f_hotspot = forms.form2()
    if f_hotspot.validate_on_submit():
        return "Submit HOTSPOT: field1: {}, field2: {}, field3: {}".format(f_hotspot.field1.data, f_hotspot.field2.data, f_hotspot.field3.data)
    return "Error with form submit"

@app.route("/volume_viewer/")
def volume_viewer():
    return flask.current_app.send_static_file('html/rendered_template/volume_viewer.html')

@app.route("/about_website/")
def about_website():
    return flask.current_app.send_static_file('html/rendered_template/about_website.html')

if __name__ == "__main__":
    socketio.run(app, debug=True)
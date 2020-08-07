from sys import modules, stderr
def validate_import(module_name):
    valid = True
    if module_name not in modules:
        print(module_name, 'was not imported', file=stderr)
        valid = False
    return valid

# Framework
import flask

# for executing terminal cmd (git)
from subprocess import Popen, PIPE, STDOUT

# Generate secret key
from os import urandom

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

# Global variables
all_exp = utils.get_all_exp()
st_dict = utils.get_struct_in_dict(all_exp)


@app.before_first_request
def render_templates():
    # get HEAD commit log
    git_cmd = Popen(['git', 'log', '-1'], stdout=PIPE, stderr=STDOUT)
    head_commit, stderr = git_cmd.communicate()
    head_commit = head_commit.decode("utf-8")
    head_commit = head_commit.split('\n')

    # home
    rendered_template = flask.render_template("html/index.html.j2",
                                              commit_info=head_commit)
    with open(app.static_folder + "/html/rendered_template/index.html", "w") as f:
        f.write(rendered_template)

    # interface
    rendered_template = flask.render_template("html/interface.html.j2",
                                              commit_info=head_commit)
    with open(app.static_folder + "/html/rendered_template/interface.html", "w") as f:
        f.write(rendered_template)

    # allen_brain
    rendered_template = flask.render_template("html/allen_brain.html.j2",
                                              all_exp=all_exp,
                                              struct_dict=st_dict,
                                              f_correlation=forms.form_correlation(),
                                              f_inj_coord=forms.form_injection_coord(),
                                              f_source=forms.form1(),
                                              f_hotspot=forms.form2(),
                                              commit_info=head_commit)
    with open(app.static_folder + "/html/rendered_template/allen_brain.html", "w") as f:
        f.write(rendered_template)

    # volume_viewer
    rendered_template = flask.render_template("html/volume_viewer.html.j2",
                                              commit_info=head_commit)
    with open(app.static_folder + "/html/rendered_template/volume_viewer.html", "w") as f:
        f.write(rendered_template)

    # about_website
    rendered_template = flask.render_template("html/about_website.html.j2",
                                              commit_info=head_commit)
    with open(app.static_folder + "/html/rendered_template/about_website.html", "w") as f:
        f.write(rendered_template)


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
        return flask.render_template("html/experiment.html.j2",
                                     exp=exp,
                                     struct=struct,
                                     prim_inj_struct=prim_inj_struct,
                                     sect_id=sect_id,
                                     sect_res=res,
                                     sect_ranges=ranges)
    else:
        # For using pre-establish filters specified in the url
        return flask.current_app.send_static_file('html/rendered_template/allen_brain.html')


@app.route("/experiments/forms/correlation_search/", methods=['POST'])
def form_correlation():
    f_correlation = forms.form_correlation()
    # error with form submit (validate_on_submit), don't know how to fix... TODO
    row = f_correlation.row.data

    structures = forms.str_to_array(f_correlation.structures.data)

    product_ids = forms.convert_array_str_to_int(forms.str_to_array(f_correlation.product_ids.data))

    hemisphere = f_correlation.hemisphere.data
    if hemisphere.upper() == "BOTH":
        hemisphere = None

    transgenic_lines = forms.str_to_array(f_correlation.transgenic_lines.data)

    injection_structures = forms.str_to_array(f_correlation.injection_structures.data)

    primary_structure_only = True
    if f_correlation.primary_structure_only.data.upper() == 'FALSE':
        primary_structure_only = False

    start_row = f_correlation.start_row.data

    num_rows = f_correlation.num_rows.data

    result, errors = utils.correlation_search(row=row,
                                              structures=structures,
                                              product_ids=product_ids,
                                              hemisphere=hemisphere,
                                              transgenic_lines=transgenic_lines,
                                              injection_structures=injection_structures,
                                              primary_structure_only=primary_structure_only,
                                              start_row=start_row,
                                              num_rows=num_rows)

    if len(errors) == 0 and isinstance(result, list):
        rendered_template = flask.render_template("xml/experiment_search.xml.j2", values=result)
        # For test
        #with open(app.static_folder + "/html/rendered_template/text1.xml", "w") as f:
        #    f.write(rendered_template)
        response = flask.make_response(rendered_template)
        response.headers['Content-Type'] = 'application/xml'
        return response

    return flask.render_template("html/experiment_search_error.html.j2",
                                 search_type="injection coordinate",
                                 xml=result,
                                 errors=errors)


@app.route("/experiments/forms/injection_coord_search/", methods=['POST'])
def form_injection_coord():
    f_inj_coord = forms.form_injection_coord()
    # error with form submit (validate_on_submit), don't know how to fix... TODO
    seed_point = [f_inj_coord.coord_x.data, f_inj_coord.coord_y.data, f_inj_coord.coord_z.data]

    product_ids = forms.convert_array_str_to_int(forms.str_to_array(f_inj_coord.product_ids.data))

    transgenic_lines = forms.str_to_array(f_inj_coord.transgenic_lines.data)

    injection_structures = forms.str_to_array(f_inj_coord.injection_structures.data)

    primary_structure_only = True
    if f_inj_coord.primary_structure_only.data.upper() == 'FALSE':
        primary_structure_only = False

    start_row = f_inj_coord.start_row.data

    num_rows = f_inj_coord.num_rows.data

    result, errors = utils.injection_correlation_search(seed_point=seed_point,
                                                        product_ids=product_ids,
                                                        transgenic_lines=transgenic_lines,
                                                        injection_structures=injection_structures,
                                                        primary_structure_only=primary_structure_only,
                                                        start_row=start_row,
                                                        num_rows=num_rows)

    if len(errors) == 0 and isinstance(result, list):
        rendered_template = flask.render_template("xml/experiment_search.xml.j2", values=result)
        response = flask.make_response(rendered_template)
        response.headers['Content-Type'] = 'application/xml'
        return response

    return flask.render_template("html/experiment_search_error.html.j2",
                                 search_type="injection coordinate",
                                 xml=result,
                                 errors=errors)


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
    app.run(debug=True)
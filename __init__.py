# Validate imported modules
from sys import modules, stderr
# Framework
import flask
# for executing terminal cmd (git)
from subprocess import Popen, PIPE, STDOUT
# Generate secret key and basic file operations
from os import urandom, path
# Get filename from path
from os.path import basename
# Application log
import logging
# Custom files
import config
import allensdk_utils as utils
import forms
import cleaner_daemon as cleaner


# Validate custom files import
def validate_import(module_name):
    valid = True
    if module_name not in modules:
        print(module_name, 'was not imported', file=stderr)
        valid = False
    return valid


validate_import('config')
validate_import('allensdk_utils')
validate_import('forms')
validate_import('cleaner_daemon')

# Global variables
st_dict = utils.get_struct_in_dict()
prod_dict = utils.get_product_dict()

# Init website
app = flask.Flask(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'
app.config["SECRET_KEY"] = urandom(24).hex()
#app.config['SERVER_NAME'] = 'xtract.com'

# Start daemon to cleanup tmp folder
daemon = cleaner.CleanupDaemon(directory=app.static_folder + path.sep + "tmp",
                               interval=config.interval,
                               dir_size=config.max_dir_size)
daemon.start()


@app.before_first_request
def render_templates():
    # get current branch name
    git_cmd = Popen(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=PIPE, stderr=STDOUT)
    branch_name, stderr_branch = git_cmd.communicate()
    branch_name = "Branch: " + branch_name.decode("utf-8")
    # get HEAD commit log
    git_cmd = Popen(['git', 'log', '-1'], stdout=PIPE, stderr=STDOUT)
    head_commit, stderr_log = git_cmd.communicate()
    head_commit = head_commit.decode("utf-8")
    head_commit = head_commit.split('\n')

    head_commit[1] = head_commit[2]
    head_commit = head_commit[:2] # only keep hash and date of change
    head_commit.insert(0, branch_name)

    # allen_brain
    struct_names, struct_acronyms = utils.get_node_list()
    rendered_template = flask.render_template("html/allen_brain.html.j2",
                                              struct_names=struct_names,
                                              struct_acronyms=struct_acronyms,
                                              all_exp=utils.all_exp,
                                              struct_dict=st_dict,
                                              prod_dict=prod_dict,
                                              f_get_csv=forms.FormExperimentsCSV(),
                                              f_correlation=forms.FormCorrelation(),
                                              f_inj_coord=forms.FormInjectionCoord(),
                                              f_source=forms.FormSource(),
                                              f_hotspot=forms.FormHotspot(),
                                              commit_info=head_commit)
    with open(app.static_folder + path.sep +
              "html" + path.sep +
              "rendered_template" + path.sep +
              "allen_brain.html", "w") as f:
        f.write(rendered_template)

    # about_website
    rendered_template = flask.render_template("html/about_website.html.j2",
                                              commit_info=head_commit)
    with open(app.static_folder + path.sep + "html" + path.sep +
              "rendered_template" + path.sep + "about_website.html", "w") as f:
        f.write(rendered_template)


@app.route("/")
def default():
    return flask.redirect(flask.url_for("home"))


@app.route("/home/")
def home():
    return flask.redirect(flask.url_for("experiments"))


@app.route("/experiments/")
def experiments():
    return flask.current_app.send_static_file("html/rendered_template/allen_brain.html")


@app.route("/experiments/<param>/")
def experiment_search(param):
    if (param.isdigit()):
        exp = utils.all_exp.loc[int(param)]
        sect_id, res, ranges = utils.get_exp_img_sections_info(param)
        return flask.render_template("html/experiment.html.j2",
                                     exp=exp,
                                     struct_dict=st_dict,
                                     prod_dict=prod_dict,
                                     sect_id=sect_id,
                                     sect_res=res,
                                     sect_ranges=ranges)
    else:
        # For using pre-establish filters specified in the url
        return flask.current_app.send_static_file("html/rendered_template/allen_brain.html")


@app.route("/experiments/forms/structures_childs/", methods=['POST'])
def structures_childs():
    acronyms = flask.request.form.getlist('acronyms[]')
    names = flask.request.form.getlist('names[]')

    result = utils.get_structures_childs(acronyms=acronyms, names=names)

    text_array = ''
    for i in range(0, len(result)):
        text_array += result[i]
        if i < len(result) - 1:
            text_array += ';'

    response = flask.make_response(text_array)
    response.headers["Content-Type"] = "text/plain"
    return response


@app.route("/experiments/forms/experiments_csv/", methods=['POST'])
def experiments_csv():
    f_get_csv = forms.FormExperimentsCSV()

    if f_get_csv.validate_on_submit():
        filtered_exp = forms.convert_array_str_to_int(forms.str_to_array(f_get_csv.filtered_exp.data))

        result, errors = utils.get_experiments_csv(experiment_ids=filtered_exp)

        response = flask.make_response(result)
        response.headers["Content-Disposition"] = "attachment; filename=experiments.csv"
        response.headers["Content-Type"] = "text/csv"
        return response

    return "<h1>400 Bad Request</h1><p>Couldn't validate form submit</p>"


@app.route("/experiments/forms/experiment_volume/", methods=['POST'])
def experiment_volume():
    experiment_id = int(flask.request.form.get('experiment'))
    img_type = flask.request.form.get('volume_type')
    res = int(flask.request.form.get('resolution'))

    file_path, errors = utils.get_experiment_volume(experiment_id=experiment_id,
                                                    img_type=img_type,
                                                    resolution=res)
    if file_path:
        return flask.current_app.send_static_file("tmp/" + basename(file_path))
    return '400 Bad Request', 400


@app.route("/experiments/forms/average_volume/", methods=['POST'])
def average_volume():
    experiment_ids = forms.convert_array_str_to_int(forms.str_to_array(flask.request.form.get('experiments')))
    res = int(flask.request.form.get('resolution'))

    file_path, errors = utils.get_average_projection_density(experiment_ids=experiment_ids, resolution=res)

    return flask.current_app.send_static_file("tmp/" + basename(file_path))


@app.route("/experiments/forms/streamlines/", methods=['POST'])
def streamlines():
    experiment_ids = forms.convert_array_str_to_int(forms.str_to_array(flask.request.form.get('experiments')))

    file_path, errors = utils.get_streamlines(experiment_ids)

    if file_path:
        return flask.current_app.send_static_file("tmp/" + basename(file_path))
    return '400 Bad Request', 400


@app.route("/experiments/forms/average_template/", methods=['POST'])
def average_template():
    res = int(flask.request.form.get('resolution'))

    file_path = utils.get_template(resolution=res)

    if file_path:
        return flask.current_app.send_static_file("tmp/" + basename(file_path))
    return '400 Bad Request', 400


@app.route("/experiments/forms/correlation_search/", methods=['POST'])
def form_correlation():
    f_correlation = forms.FormCorrelation()

    # error with form submit (validate_on_submit), don't know how to fix... TODO
    if f_correlation.validate_on_submit():
        return "You're a wizard Harry"

    row = f_correlation.row.data

    structures = forms.str_to_array(f_correlation.structures.data)

    hemisphere = f_correlation.hemisphere.data
    if hemisphere.upper() == "BOTH":
        hemisphere = None

    transgenic_lines = forms.str_to_array(f_correlation.transgenic_lines.data)

    injection_structures = forms.str_to_array(f_correlation.injection_structures.data)

    primary_structure_only = True
    if f_correlation.primary_structure_only.data.upper() == 'FALSE':
        primary_structure_only = False

    product_ids = forms.convert_array_str_to_int(forms.str_to_array(f_correlation.product_ids.data))

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
        rendered_template = flask.render_template("xml/experiment_search.xml.j2",
                                                  elem="experiment",
                                                  values=result)
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
    f_inj_coord = forms.FormInjectionCoord()

    # error with form submit (validate_on_submit), don't know how to fix... TODO
    if f_inj_coord.validate_on_submit():
        return "You're a wizard Harry"

    seed_point = [f_inj_coord.coord_x.data, f_inj_coord.coord_y.data, f_inj_coord.coord_z.data]

    transgenic_lines = forms.str_to_array(f_inj_coord.transgenic_lines.data)

    injection_structures = forms.str_to_array(f_inj_coord.injection_structures.data)

    primary_structure_only = True
    if f_inj_coord.primary_structure_only.data.upper() == 'FALSE':
        primary_structure_only = False

    product_ids = forms.convert_array_str_to_int(forms.str_to_array(f_inj_coord.product_ids.data))

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
        rendered_template = flask.render_template("xml/experiment_search.xml.j2",
                                                  elem="experiment",
                                                  values=result)
        response = flask.make_response(rendered_template)
        response.headers['Content-Type'] = 'application/xml'
        return response

    return flask.render_template("html/experiment_search_error.html.j2",
                                 search_type="injection coordinate",
                                 xml=result,
                                 errors=errors)


@app.route("/experiments/forms/source/", methods=['POST'])
def form_source():
    f_source = forms.FormSource()

    # error with form submit (validate_on_submit), don't know how to fix... TODO
    if f_source.validate_on_submit():
        return "You're a wizard Harry"

    injection_structures = forms.str_to_array(f_source.injection_structures.data)

    target_domain = forms.str_to_array(f_source.target_domain.data)

    injection_hemisphere = f_source.injection_hemisphere.data
    if injection_hemisphere.upper() == "BOTH":
        injection_hemisphere = None

    target_hemisphere = f_source.target_hemisphere.data
    if target_hemisphere.upper() == "BOTH":
        target_hemisphere = None

    transgenic_lines = forms.str_to_array(f_source.transgenic_lines.data)

    injection_domain = forms.str_to_array(f_source.injection_domain.data)

    primary_structure_only = True
    if f_source.primary_structure_only.data.upper() == 'FALSE':
        primary_structure_only = False

    product_ids = forms.convert_array_str_to_int(forms.str_to_array(f_source.product_ids.data))

    start_row = f_source.start_row.data

    num_rows = f_source.num_rows.data

    result, errors = utils.source_search(injection_structures=injection_structures,
                                         target_domain=target_domain,
                                         injection_hemisphere=injection_hemisphere,
                                         target_hemisphere=target_hemisphere,
                                         transgenic_lines=transgenic_lines,
                                         injection_domain=injection_domain,
                                         primary_structure_only=primary_structure_only,
                                         product_ids=product_ids,
                                         start_row=start_row,
                                         num_rows=num_rows)

    if len(errors) == 0 and isinstance(result, list):
        rendered_template = flask.render_template("xml/experiment_search.xml.j2",
                                                  elem="experiment",
                                                  values=result)
        response = flask.make_response(rendered_template)
        response.headers['Content-Type'] = 'application/xml'
        return response

    return flask.render_template("html/experiment_search_error.html.j2",
                                 search_type="injection coordinate",
                                 xml=result,
                                 errors=errors)


@app.route("/experiments/forms/hotspot/", methods=['POST'])
def form_hotspot():
    f_hotspot = forms.FormHotspot()

    if f_hotspot.validate_on_submit():
        rows = forms.convert_array_str_to_int(forms.str_to_array(f_hotspot.rows.data))

        injection_structures = forms.str_to_array(f_hotspot.injection_structures.data)

        depth = f_hotspot.depth.data
        if depth.upper() == "NONE":
            depth = None

        probabilities, matrix, rows, labels, errors = utils.hotspot_search(rows=rows,
                                                                           injection_structures=injection_structures,
                                                                           depth=depth)

        return flask.render_template("html/hotspot_search.html.j2",
                                     probabilities=probabilities,
                                     matrix=matrix,
                                     rows=rows,
                                     labels=labels,
                                     errors=errors)

    return "<h1>400 Bad Request</h1><p>Couldn't validate form submit</p>"


@app.route("/about_website/")
def about_website():
    return flask.current_app.send_static_file("html/rendered_template/about_website.html")


if __name__ == "__main__":
    # For logging
    #logging.basicConfig(filename='app.log', level=logging.DEBUG)

    app.run(host=config.address, port=config.port, debug=config.debug)
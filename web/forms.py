from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, StringField, SelectField, SubmitField, FieldList, FormField
# For regex validation in input field
# from wtforms.validators import Regexp


def str_to_array(str):
    array = []
    str_split = str.split(';')
    for elem in str_split:
        trimmed_elem = elem.strip(' ')
        # Add to array if elem isn't empty
        if trimmed_elem:
            array.append(trimmed_elem)
    if len(array) == 0:
        return None
    return array


def convert_array_str_to_int(strArray):
    if strArray is None:
        return None
    return [int(string) for string in strArray]


class FormExperimentsCSV(FlaskForm):
    # (list of integers or strings) SectionDataSet.id to correlate against
    filtered_exp = StringField("experiment ids: *", render_kw={"placeholder": "id_1; id_2; ..."})
    # submit btn
    submit_exp_csv = SubmitField("download csv")


class FormCorrelation(FlaskForm):
    # https://allensdk.readthedocs.io/en/latest/allensdk.api.queries.mouse_connectivity_api.html#allensdk.api.queries.mouse_connectivity_api.MouseConnectivityApi.experiment_correlation_search

    # (integer) SectionDataSet.id to correlate against
    row = IntegerField("experiment id: *", render_kw={"placeholder": "id"})
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    structures = StringField("list of structures name or acronym:",
                             render_kw={"placeholder": "struct_1; struct_2; ..."})
    # (string, optional) Use ‘right’ or ‘left’. Defaults to both hemispheres.
    hemisphere = SelectField("hemisphere:", choices=["both", "left", "right"])
    # (list of integers or strings, optional) Integer TransgenicLine.id or String TransgenicLine.name.
    # Specify ID 0 to exclude all TransgenicLines.
    transgenic_lines = StringField("transgenic lines:", render_kw={"placeholder": "line_1; line_2; ..."})
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    injection_structures = StringField("injection structures:", render_kw={"placeholder": "struct_1; struct_2; ..."})
    # (boolean, optional)
    primary_structure_only = SelectField("primary structure only:", choices=["True", "False"])
    # (list of integers, optional) Integer Product.id
    product_ids = StringField("product_ids:", render_kw={"placeholder": "id_1; id_2; ..."})
    # (integer, optional) For paging purposes. Defaults to 0
    start_row = IntegerField("start row:", render_kw={"placeholder": "0"})
    # (integer, optional) For paging purposes. Defaults to 2000
    num_rows = IntegerField("num rows:", render_kw={"placeholder": "2000"})
    # submit btn
    submit_correlation = SubmitField("submit")


class FormInjectionCoord(FlaskForm):
    # https://allensdk.readthedocs.io/en/latest/allensdk.api.queries.mouse_connectivity_api.html#allensdk.api.queries.mouse_connectivity_api.MouseConnectivityApi.experiment_injection_coordinate_search

    # (list of integers) The coordinates of a point in 3-D SectionDataSet space
    coord_x = IntegerField("Axe Antérieur / Postérieur: *", render_kw={"placeholder": "0"})
    coord_y = IntegerField("Axe Supérieur / Inférieur: *", render_kw={"placeholder": "0"})
    coord_z = IntegerField("Axe Droite / Gauche: *", render_kw={"placeholder": "0"})
    # (list of integers or strings, optional) Integer TransgenicLine.id or String TransgenicLine.name.
    # Specify ID 0 to exclude all TransgenicLines.
    transgenic_lines = StringField("transgenic lines:", render_kw={"placeholder": "line_1; line_2; ..."})
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    injection_structures = StringField("injection structures:", render_kw={"placeholder": "struct_1; struct_2; ..."})
    # (boolean, optional)
    primary_structure_only = SelectField("primary structure only:", choices=["True", "False"])
    # (list of integers, optional) Integer Product.id
    product_ids = StringField("product_ids:", render_kw={"placeholder": "id_1; id_2; ..."})
    # (integer, optional) For paging purposes. Defaults to 0
    start_row = IntegerField("start row:", render_kw={"placeholder": "0"})
    # (integer, optional) For paging purposes. Defaults to 2000
    num_rows = IntegerField("num rows:", render_kw={"placeholder": "2000"})
    # submit btn
    submit_injection_coord = SubmitField("submit")


class FormSource(FlaskForm):
    # https://allensdk.readthedocs.io/en/latest/allensdk.api.queries.mouse_connectivity_api.html#allensdk.api.queries.mouse_connectivity_api.MouseConnectivityApi.experiment_source_search

    # (list of integers or strings) Integer Structure.id or String Structure.acronym
    injection_structures = StringField("injection structures: *", render_kw={"placeholder": "struct_1; struct_2; ..."})
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    target_domain = StringField("target domains:", render_kw={"placeholder": "struct_1; struct_2; ..."})
    # (string, optional) Use ‘right’ or ‘left’. Defaults to both hemispheres.
    injection_hemisphere = SelectField("injection hemisphere:", choices=["both", "left", "right"])
    # (string, optional) Use ‘right’ or ‘left’. Defaults to both hemispheres.
    target_hemisphere = SelectField("target hemisphere:", choices=["both", "left", "right"])
    # (list of integers or strings, optional) Integer TransgenicLine.id or String TransgenicLine.name. Specify ID 0 to exclude all TransgenicLines.
    transgenic_lines = StringField("transgenic lines:", render_kw={"placeholder": "line_1; line_2; ..."})
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    injection_domain = StringField("injection domains:", render_kw={"placeholder": "struct_1; struct_2; ..."})
    # (boolean, optional)
    primary_structure_only = SelectField("primary structure only:", choices=["True", "False"])
    # (list of integers, optional) Integer Product.id
    product_ids = StringField("product_ids:", render_kw={"placeholder": "id_1; id_2; ..."})
    # (integer, optional) For paging purposes. Defaults to 0
    start_row = IntegerField("start row:", render_kw={"placeholder": "0"})
    # (integer, optional) For paging purposes. Defaults to 2000
    num_rows = IntegerField("num rows:", render_kw={"placeholder": "2000"})
    # submit btn
    submit_source = SubmitField("submit")


class FormHotspot(FlaskForm):
    # (list of integers or strings) SectionDataSet.id to correlate against
    rows = StringField("experiment ids: *", render_kw={"placeholder": "id_1; id_2; ..."})
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    injection_structures = StringField("injection structures:", render_kw={"placeholder": "struct_1; struct_2; ..."})
    # (string, optional) Use ‘right’ or ‘left’. Defaults to both hemispheres.
    depth = SelectField("structures depth:", choices=["none", "child", "all"])
    # submit btn
    submit_hotspot = SubmitField("submit")

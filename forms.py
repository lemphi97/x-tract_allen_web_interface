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
    return {int(string) for string in strArray}


class form_correlation(FlaskForm):
    # https://allensdk.readthedocs.io/en/latest/allensdk.api.queries.mouse_connectivity_api.html#allensdk.api.queries.mouse_connectivity_api.MouseConnectivityApi.experiment_correlation_search

    # (intger) SectionDataSet.id to correlate against
    row = IntegerField("experiment id: *")
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    structures = StringField("list of structures name or acronym:")
    # (string, optional) Use ‘right’ or ‘left’. Defaults to both hemispheres.
    hemisphere = SelectField("hemisphere:", choices=["both", "left", "right"])
    # (list of integers or strings, optional) Integer TransgenicLine.id or String TransgenicLine.name. Specify ID 0 to exclude all TransgenicLines.
    transgenic_lines = StringField("transgenic lines:")
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    injection_structures = StringField("injection structures:")
    # (boolean, optional)
    primary_structure_only = SelectField("primary structure only:", choices=["True", "False"])
    # (list of integers, optional) Integer Product.id
    product_ids = StringField("product_ids:")
    # (integer, optional) For paging purposes. Defaults to 0
    start_row = IntegerField("start row:")
    # (integer, optional) For paging purposes. Defaults to 2000
    num_rows = IntegerField("num rows:")
    # submit btn
    submit_correlation = SubmitField("submit")


class form_injection_coord(FlaskForm):
    # https://allensdk.readthedocs.io/en/latest/allensdk.api.queries.mouse_connectivity_api.html#allensdk.api.queries.mouse_connectivity_api.MouseConnectivityApi.experiment_injection_coordinate_search

    # (list of integers) The coordinates of a point in 3-D SectionDataSet space
    coord_x = IntegerField("Axe Antérieur / Postérieur: *")
    coord_y = IntegerField("Axe Supérieur / Inférieur: *")
    coord_z = IntegerField("Axe Droite / Gauche: *")
    # (list of integers or strings, optional) Integer TransgenicLine.id or String TransgenicLine.name. Specify ID 0 to exclude all TransgenicLines.
    transgenic_lines = StringField("transgenic lines:")
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    injection_structures = StringField("injection structures:")
    # (boolean, optional)
    primary_structure_only = SelectField("primary structure only:", choices=["True", "False"])
    # (list of integers, optional) Integer Product.id
    product_ids = StringField("product_ids:")
    # (integer, optional) For paging purposes. Defaults to 0
    start_row = IntegerField("start row:")
    # (integer, optional) For paging purposes. Defaults to 2000
    num_rows = IntegerField("num rows:")
    # submit btn
    submit_injection_coord = SubmitField("submit")


class form_source(FlaskForm):
    # https://allensdk.readthedocs.io/en/latest/allensdk.api.queries.mouse_connectivity_api.html#allensdk.api.queries.mouse_connectivity_api.MouseConnectivityApi.experiment_source_search

    # (list of integers or strings) Integer Structure.id or String Structure.acronym
    injection_structures = StringField("injection structures: *")
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    target_domain = StringField("target domains:")
    # (string, optional) Use ‘right’ or ‘left’. Defaults to both hemispheres.
    injection_hemisphere = SelectField("injection hemisphere:", choices=["both", "left", "right"])
    # (string, optional) Use ‘right’ or ‘left’. Defaults to both hemispheres.
    target_hemisphere = SelectField("target hemisphere:", choices=["both", "left", "right"])
    # (list of integers or strings, optional) Integer TransgenicLine.id or String TransgenicLine.name. Specify ID 0 to exclude all TransgenicLines.
    transgenic_lines = StringField("transgenic lines:")
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    injection_domain = StringField("injection domains:")
    # (boolean, optional)
    primary_structure_only = SelectField("primary structure only:", choices=["True", "False"])
    # (list of integers, optional) Integer Product.id
    product_ids = StringField("product_ids:")
    # (integer, optional) For paging purposes. Defaults to 0
    start_row = IntegerField("start row:")
    # (integer, optional) For paging purposes. Defaults to 2000
    num_rows = IntegerField("num rows:")
    # submit btn
    submit_source = SubmitField("submit")


class form_hotspot(FlaskForm):
    # (list of integers or strings) SectionDataSet.id to correlate against
    rows = StringField("experiment ids: *")
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    injection_structures = StringField("injection structures:")
    # (string, optional) Use ‘right’ or ‘left’. Defaults to both hemispheres.
    depth = SelectField("structures depth:", choices=["none", "child", "all"])
    # submit btn
    submit_hotspot = SubmitField("submit")

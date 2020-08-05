from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SelectField, SubmitField
# For regex validation in input field
#from wtforms.validators import Regexp

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
    submit = SubmitField("submit")

class form_inj_coord(FlaskForm):
    ...

class form_source(FlaskForm):
    ...

class form_hotspot(FlaskForm):
    ...

class form1(FlaskForm):
    field1 = StringField("field1")
    field2 = StringField("field2")

class form2(FlaskForm):
    field1 = StringField("field1")
    field2 = StringField("field2")
    field3 = StringField("field3")
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SelectField, SubmitField
from wtforms.validators import Regexp

class f_correlation(FlaskForm):
    # https://allensdk.readthedocs.io/en/latest/allensdk.api.queries.mouse_connectivity_api.html#allensdk.api.queries.mouse_connectivity_api.MouseConnectivityApi.experiment_correlation_search
    row = IntegerField("experiment id")
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    structures = StringField("list of structures name or acronym")
    # (string, optional) Use ‘right’ or ‘left’. Defaults to both hemispheres.
    hemisphere = SelectField("hemisphere", choices=["left", "right", "both"])
    # (list of integers or strings, optional) Integer TransgenicLine.id or String TransgenicLine.name. Specify ID 0 to exclude all TransgenicLines.
    transgenic_lines = StringField("transgenic lines")
    # (list of integers or strings, optional) Integer Structure.id or String Structure.acronym
    injection_structures = StringField("injection structures")
    # (boolean, optional)
    primary_structure_only = SelectField("primary structure only", choices=["True", "False"])
    # (list of integers, optional) Integer Product.id
    product_ids = StringField("product_ids")
    # (integer, optional) For paging purposes. Defaults to 0
    start_row = IntegerField("start row")
    # (integer, optional) For paging purposes. Defaults to 2000
    num_rows = IntegerField("num rows")

class f_inj_coord(FlaskForm):
    ...

class f_source(FlaskForm):
    ...

class f_hotspot(FlaskForm):
    ...

class form1(FlaskForm):
    field1 = StringField("field1")
    field2 = StringField("field2")

class form2(FlaskForm):
    field1 = StringField("field1")
    field2 = StringField("field2")
    field3 = StringField("field3")
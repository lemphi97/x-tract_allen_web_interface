# This file is for handling Interactions with allensdk

# Get experiments data
from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache
# Download experiment nrrd and png files
from allensdk.api.queries.image_download_api import ImageDownloadApi
from allensdk.api.queries.ontologies_api import OntologiesApi
# Search functions for experiments
from allensdk.api.queries.mouse_connectivity_api import MouseConnectivityApi

import pandas as pd
from allensdk.api.queries import grid_data_api
import numpy as np
from pathlib import Path
import urllib.request
import json

mcc = MouseConnectivityCache()
mca = MouseConnectivityApi()
st_tree = mcc.get_structure_tree()
image_api = ImageDownloadApi()
all_exp = None # is set later
dict_struct_id = st_tree.get_name_map()
dict_struct_acron = st_tree.get_id_acronym_map()
dict_struct_name = {v: k for k, v in dict_struct_id.items()}


# return all structure in a dict (key: id, value: name with acronym)
def exp_save_nrrd(exp_id, img=[], res=100, folder="."):
    '''
    Download in NRRD format.

        Parameters
        ----------
        exp_id : integer
            What to download.
        img : list of strings, optional
            Image volume. 'projection_density', 'projection_energy', 'injection_fraction', 'injection_density', 'injection_energy', 'data_mask'.
        res : integer, optional
            in microns. 10, 25, 50, or 100 (default).
        folder : string, optional
            Folder name to save file(s) into.

        Return
        ------
        files_path : list of string
            paths of downloaded nrrd file(s)
    '''
    Path(folder).mkdir(parents=True, exist_ok=True)
    files_path = []
    gd_api = grid_data_api.GridDataApi(resolution=res)
    for img_type in img:
        # download nrrd files
        save_file_path = f"{folder}/{exp_id}_{img_type}_{res}.nrrd"
        gd_api.download_projection_grid_data(
            exp_id,
            image=[img_type],
            resolution=res,
            save_file_path=save_file_path
        )
        files_path.append(save_file_path)
    return files_path


def get_struct_in_dict(experiences):
    st_dict = {}

    for i in range(0, len(experiences)):
        index_val = experiences.iloc[i]
        struct_id_array = index_val['injection_structures']

        for struct_id in struct_id_array:
            if struct_id not in st_dict:
                struct_dict = st_tree.get_structures_by_id([struct_id])[0]
                st_dict[struct_id] = struct_dict['name'] + " |" + struct_dict['acronym'] + "|"

    return st_dict


def get_all_exp():
    cre_neg_exp = mcc.get_experiments(dataframe=True, cre=False)
    cre_neg_exp['cre'] = np.zeros((len(cre_neg_exp), 1), dtype=bool)

    cre_pos_exp = mcc.get_experiments(dataframe=True, cre=True)
    cre_pos_exp['cre'] = np.ones((len(cre_pos_exp), 1), dtype=bool)

    return pd.concat([cre_neg_exp, cre_pos_exp])


all_exp = get_all_exp()


def get_product_dict():
    product_list = {}
    with urllib.request.urlopen("http://api.brain-map.org/api/v2/data/query.json?criteria=model::Product") as url:
        product_list = json.loads(url.read().decode())['msg']

    product_dict = {}
    for product in product_list:
        product_dict[product['id']] = product

    return product_dict


def get_exp_img_sections_info(exp_id):
    # res and ranges don't seem to change from section to section.
    # To cut down on exec time, I'll assume they never do
    sections = image_api.section_image_query(exp_id)
    sections_dict = {}
    sections_id = []
    default_res = sections[0]["resolution"]
    # image_api.get_section_image_ranges takes about 0.5 sec each calls so use it wisely
    default_ranges = image_api.get_section_image_ranges([sections[0]["id"]])[0]
    foo = default_ranges[3]
    default_ranges[2] = foo
    default_ranges[3] = foo * 2

    # section number do not always start from 0 and might not always increment by 1
    for i in range(0, len(sections)):
        sections_dict[sections[i]["section_number"]] = sections[i]["id"]

    for key in sorted(sections_dict.keys()):
        sections_id.append(sections_dict[key])

    return sections_id, default_res, default_ranges


def get_experiments_csv(experiments_id):
    filter_dict = {}
    errors = []

    if experiments_id is not None:
        for exp_id in experiments_id:
            if exp_id in all_exp.index:
                filter_dict[exp_id]=all_exp.loc[exp_id]
            else:
                errors.append(exp_id + " does not exist")

    df = pd.DataFrame.from_dict(filter_dict, orient="index")
    csv = df.to_csv()

    return csv, errors


def validate_structures(structures, errors, category):
    if structures is not None:
        for i in range(0, len(structures)):
            exist = True
            struct = structures[i]
            if struct.isdigit():
                struct = int(struct)
                structures[i] = struct
                if struct not in dict_struct_id:
                    exist = False
            elif struct in dict_struct_name:
                structures[i] = dict_struct_name[struct]
            elif struct not in dict_struct_acron:
                exist = False
            if not exist:
                errors.append(category + " |" + str(struct) + "| doesn't exist")
    return


def validate_hemisphere(hemisphere, errors, category):
    if hemisphere is not None:
        hemisphere = hemisphere.lower()
    if hemisphere not in ["left", "right", None]:
        errors.append(category + " |" + str(hemisphere) + "| is invalid")
    return


def correlation_search(row,                          # Integer
                       structures=None,              # [String], None
                       product_ids=None,             # [Integer], None
                       hemisphere=None,              # 'left', 'right', None
                       transgenic_lines=None,        # [String], None, Specify ID '0' to exclude all TransgenicLines.
                       injection_structures=None,    # [String], None
                       primary_structure_only=None,  # True, False, None
                       start_row=None,               # Integer, None
                       num_rows=None):               # Integer, None
    errors = []

    if row not in mcc.get_experiments(dataframe=True)['id']:
        errors.append("experiment |" + str(row) + "| doesn't exist")

    validate_structures(structures=structures, errors=errors, category="structure")

    validate_structures(structures=injection_structures, errors=errors, category="injection structures")

    validate_hemisphere(hemisphere=hemisphere, errors=errors, category="hemisphere")

    # I don't know how to validate product id beforehand
    # I don't know how to validate transgenic line beforehand
    if transgenic_lines is not None:
        for i in range(0, len(transgenic_lines)):
            line = transgenic_lines[i]
            if line.isdigit():
                transgenic_lines[i] = line

    result = mca.experiment_correlation_search(row=row,
                                               structures=structures,
                                               injection_structures=injection_structures,
                                               product_ids=product_ids,
                                               hemisphere=hemisphere,
                                               transgenic_lines=transgenic_lines,
                                               primary_structure_only=primary_structure_only,
                                               start_row=start_row,
                                               num_rows=num_rows)

    return result, errors


def injection_correlation_search(seed_point,                   # [Integer]
                                 product_ids=None,             # [Integer], None
                                 transgenic_lines=None,        # [String], None, Specify ID '0' to exclude all TransgenicLines.
                                 injection_structures=None,    # [String], None
                                 primary_structure_only=None,  # Boolean, None
                                 start_row=None,               # Integer, None
                                 num_rows=None):               # Integer, None
    errors = []

    coord_maximums = [13100, 7800, 11300]
    coord_axis = ['x', 'y', 'z']
    for i in range(0, 3):
        if seed_point[i] < 0 or seed_point[i] > coord_maximums[i]:
            errors.append("coordonate " + coord_axis[i] +
                          " (0, " + coord_maximums[i] +
                          ") is out of bound |" + seed_point[i] + "|")

    validate_structures(structures=injection_structures, errors=errors, category="injection structures")

    # I don't know how to validate product id beforehand
    # I don't know how to validate transgenic line beforehand
    if transgenic_lines is not None:
        for i in range(0, len(transgenic_lines)):
            line = transgenic_lines[i]
            if line.isdigit():
                transgenic_lines[i] = line

    result = mca.experiment_injection_coordinate_search(seed_point=seed_point,
                                                        injection_structures=injection_structures,
                                                        product_ids=product_ids,
                                                        transgenic_lines=transgenic_lines,
                                                        primary_structure_only=primary_structure_only,
                                                        start_row=start_row,
                                                        num_rows=num_rows)

    return result, errors


def source_search(injection_structures,         # [String], None
                  target_domain=None,           # [String], None
                  injection_hemisphere=None,    # String, None
                  target_hemisphere=None,       # String, None
                  transgenic_lines=None,        # [String], None
                  injection_domain=None,        # [String], None
                  primary_structure_only=None,  # Boolean, None
                  product_ids=None,             # [Integer], None
                  start_row=None,               # Integer, None
                  num_rows=None):               # Integer, None
    errors = []

    validate_structures(structures=injection_structures, errors=errors, category="injection structures")

    validate_structures(structures=target_domain, errors=errors, category="target domain")

    validate_structures(structures=injection_domain, errors=errors, category="injection domain")

    validate_hemisphere(hemisphere=injection_hemisphere, errors=errors, category="injection hemisphere")

    validate_hemisphere(hemisphere=target_hemisphere, errors=errors, category="target hemisphere")

    # I don't know how to validate product id beforehand
    # I don't know how to validate transgenic line beforehand
    if transgenic_lines is not None:
        for i in range(0, len(transgenic_lines)):
            line = transgenic_lines[i]
            if line.isdigit():
                transgenic_lines[i] = line

    result = mca.experiment_source_search(injection_structures=injection_structures,
                                          target_domain=target_domain,
                                          injection_hemisphere=injection_hemisphere,
                                          target_hemisphere=target_hemisphere,
                                          transgenic_lines=transgenic_lines,
                                          injection_domain=injection_domain,
                                          primary_structure_only=primary_structure_only,
                                          product_ids=product_ids,
                                          start_row=start_row,
                                          num_rows=num_rows)

    return result, errors


def hotspot_search(rows,                  # [Integer]
                   injection_structures,  # [String, Integer], None
                   depth):                # String
    errors = []

    all_exp_id = mcc.get_experiments(dataframe=True)['id']
    for row in rows:
        if row not in all_exp_id:
            errors.append("experiment |" + str(row) + "| doesn't exist")

    structures_id = []
    if injection_structures is not None:
        for struct in injection_structures:
            structure_id = None
            if struct in dict_struct_id:
                structure_id = struct
            elif struct in dict_struct_acron:
                structure_id = dict_struct_acron[struct]
            elif struct in dict_struct_name:
                structure_id = dict_struct_name[struct]
            else:
                errors.append("structure |" + str(struct) + "| doesn't exist")

            if structure_id is not None and structure_id not in structures_id:
                structures_id.append(structure_id)
            if depth == 'child':
                structure_childs = st_tree.child_ids([structure_id])[0]
                structures_id.extend(struct for struct in structure_childs if struct not in structures_id)
            elif depth == 'all':
                structure_descendants = st_tree.descendant_ids([structure_id])[0]
                structures_id.extend(struct for struct in structure_descendants if struct not in structures_id)

    if len(structures_id) == 0:
        structures_id = None

    # connectivity matrix
    pm = mcc.get_projection_matrix(experiment_ids=rows,
                                   projection_structure_ids=structures_id,
                                   parameter="projection_density")

    matrix = np.nan_to_num([i for i in pm['matrix']])

    # Normalize density
    projection_probability = []
    for density in matrix:
        projection_probability.append(density / density.sum())

    projection_crossing = projection_probability[0]
    for i in range(1, len(projection_probability)):
        projection_crossing *= projection_probability[i]

    dict_proj_crossing = {}
    for i in range(0, len(projection_crossing)):
        dict_proj_crossing[pm['columns'][i]['label']] = projection_crossing[i]

    # numpy array to list array (for templates uses)
    matrix = [list(array) for array in matrix]

    return dict_proj_crossing, matrix, list(pm['rows']), [c['label'] for c in pm['columns']], errors

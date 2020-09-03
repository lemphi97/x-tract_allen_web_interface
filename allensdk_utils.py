# This file is for handling Interactions with allensdk

import pandas as pd
import numpy as np
from pathlib import Path
import uuid
import urllib.request
import json
import nrrd
import nibabel as nib

# Get experiments data
from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache
# Download experiment nrrd and png files
from allensdk.api.queries.image_download_api import ImageDownloadApi
from allensdk.api.queries.ontologies_api import OntologiesApi
# Search functions for experiments
from allensdk.api.queries.mouse_connectivity_api import MouseConnectivityApi
# Download experiment volume
from allensdk.api.queries import grid_data_api
# Download tractography
import streamlines

# paths
model_path = "web/static/models"
tmp_path = "web/static/tmp"

mcc = MouseConnectivityCache()
mca = MouseConnectivityApi()
st_tree = mcc.get_structure_tree()
image_api = ImageDownloadApi()
all_exp = None # is set later
dict_struct_name_id = st_tree.get_name_map()
dict_struct_name = {v.upper(): k for k, v in dict_struct_name_id.items()}
dict_struct_acron = {k.upper(): v for k, v in st_tree.get_id_acronym_map().items()}
dict_struct_acron_id = {v: k for k, v in dict_struct_acron.items()}


def get_all_exp():
    cre_neg_exp = mcc.get_experiments(dataframe=True, cre=False)
    cre_neg_exp['cre'] = np.zeros((len(cre_neg_exp), 1), dtype=bool)

    cre_pos_exp = mcc.get_experiments(dataframe=True, cre=True)
    cre_pos_exp['cre'] = np.ones((len(cre_pos_exp), 1), dtype=bool)

    return pd.concat([cre_neg_exp, cre_pos_exp]).round(5)


all_exp = get_all_exp()


def nrrd_to_nifti(nrrd_array, res):
    affine = np.zeros((4,4))
    affine[0,2] = res * 1e-3
    affine[1,0] = -res * 1e-3
    affine[2,1] = -res * 1e-3
    affine[3,3] = 1

    nifti_volume = nib.Nifti1Image(nrrd_array, affine)
    file_path = tmp_path + "/" + "nifti_volume_" + str(res) + "_" + uuid.uuid4().hex + ".nii"
    nib.save(nifti_volume, file_path)

    return file_path


# get all structures in a dict (key: id, value: name with acronym)
def get_struct_in_dict():
    st_dict = {}

    for i in range(0, len(all_exp)):
        index_val = all_exp.iloc[i]
        struct_ids = index_val['injection_structures']

        for struct_id in struct_ids:
            if struct_id not in st_dict:
                struct_dict = st_tree.get_structures_by_id([struct_id])[0]
                st_dict[struct_id] = struct_dict['name'] + " |" + struct_dict['acronym'] + "|"

    return st_dict


# get the minimum of nodes/structures in 2 lists (names, acron).
# Meant for the autocomplete options on client side.
def get_node_list():
    node_list = set()

    for i in range(0, len(all_exp)):
        index_val = all_exp.iloc[i]

        struct_ids = index_val['injection_structures']
        for struct_id in struct_ids:
            # check if node as already been done to save time on ancestor search
            if struct_id not in node_list:
                node_list.add(struct_id)
                ancestor_ids_list = st_tree.ancestor_ids([struct_id])

                # Concatenate lists in ancestor_ids
                ancestor_ids = set()
                for list in ancestor_ids_list:
                    for elem in list:
                        ancestor_ids.add(elem)

                for ancestor_id in ancestor_ids:
                    if ancestor_id not in node_list:
                        node_list.add(ancestor_id)

    node_dictionaries = st_tree.nodes(node_list)

    name_list = []
    acronym_list = []
    for node_dict in node_dictionaries:
        name_list.append(node_dict['name'])
        acronym_list.append(node_dict['acronym'])

    return name_list, acronym_list


# returns product dictionary (key: id, value: dict about product)
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


def get_structures_childs(acronyms, names):
    '''
    Get valid structures childs in a list.

        Parameters
        ----------
        acronyms : list of strings
            Structures acronyms.
        names : list of strings
            Structures names.

        Return
        ------
        structures_childs : list of string
            Child structures from acronyms and names. Each element is an acronym.
    '''
    structures_childs_id = []

    if acronyms is not None:
        for struct in acronyms:
            struct_uppercase = struct.upper().strip(" ")
            if struct_uppercase in dict_struct_acron:
                structure_childs = st_tree.descendant_ids([dict_struct_acron[struct_uppercase]])[0]
                structures_childs_id.extend(child_id for child_id in structure_childs
                                            if child_id not in structures_childs_id and
                                            child_id != dict_struct_acron[struct_uppercase])

    if names is not None:
        for struct in names:
            struct_uppercase = struct.upper().strip(" ")
            if struct_uppercase in dict_struct_name:
                structure_childs = st_tree.descendant_ids([dict_struct_name[struct_uppercase]])[0]
                structures_childs_id.extend(child_id for child_id in structure_childs
                                            if child_id not in structures_childs_id and
                                            child_id != dict_struct_name[struct_uppercase])

    # structure ids to acronyms
    structures_childs = []
    for struct_id in structures_childs_id:
        structures_childs.append(dict_struct_acron_id[struct_id])

    return structures_childs


def get_experiments_csv(experiment_ids):
    filter_dict = {}
    errors = []

    if experiment_ids is not None:
        for exp_id in experiment_ids:
            if exp_id in all_exp.index:
                filter_dict[exp_id]=all_exp.loc[exp_id]
            else:
                errors.append(exp_id + " does not exist")

    df = pd.DataFrame.from_dict(filter_dict, orient="index")
    csv = df.to_csv()

    return csv, errors


def get_experiment_volume(experiment_id, img_type, resolution):
    '''
    Download in nifti format.

        Parameters
        ----------
        experiment_id : integer
            What to download.
        img_type : a strings
            Image volume. 'projection_density',
                          'projection_energy',
                          'injection_fraction',
                          'injection_density',
                          'injection_energy',
                          'data_mask'.
        resolution : integer, optional
            in microns. 10, 25, 50, or 100 (default).

        Return
        ------
        file_path : string
            path of created nifti file
    '''
    allowed_img_types = ['projection_density',
                         'projection_energy',
                         'injection_fraction',
                         'injection_density',
                         'injection_energy',
                         'data_mask']
    errors = []
    if img_type in allowed_img_types:
        gd_api = grid_data_api.GridDataApi(resolution=resolution)

        # download nrrd files
        save_file_path = tmp_path + f"/{experiment_id}_{img_type}_{resolution}.nrrd"
        gd_api.download_projection_grid_data(
            experiment_id,
            image=[img_type],
            resolution=resolution,
            save_file_path=save_file_path
        )

        return nrrd_to_nifti(nrrd.read(save_file_path)[0], resolution), errors
    else:
        errors.append(img_type + " image type doesn't exist")
    return None, errors


def get_average_projection_density(experiment_ids, resolution):
    mcc.resolution = resolution  # [10. 25. 50. 100]
    errors = []

    template = mcc.get_template_volume(file_name=model_path + "/average_template_" +
                                                 str(mcc.resolution) + ".nrrd")[0]
    vol_avg = np.zeros_like(template, dtype='float32')

    valid_experiment_ids = []
    if experiment_ids is not None:
        for exp_id in experiment_ids:
            if exp_id in all_exp.index:
                valid_experiment_ids.append(exp_id)
            else:
                errors.append(exp_id + " does not exist")

    if valid_experiment_ids is not None:
        for exp_id in valid_experiment_ids:
            vol_avg += mcc.get_projection_density(
                experiment_id=exp_id,
                file_name=tmp_path + "/" + str(exp_id) +
                          "_projection_density_" +
                          str(mcc.resolution) + ".nrrd"
            )[0] / len(valid_experiment_ids)

    file_path = nrrd_to_nifti(vol_avg, mcc.resolution)

    return file_path, errors


def get_streamlines(experiment_ids):
    sapi = streamlines.StreamLines(directory=tmp_path)
    tractogram_path = None
    errors = []

    if experiment_ids:
        # Check if we have valid experiments
        for exp_id in experiment_ids:
            if exp_id not in mcc.get_experiments(dataframe=True)['id']:
                errors.append("experiment |" + str(exp_id) + "| doesn't exist")
            else:
                sapi.download(experiment_ids)

    if len(sapi.data) > 0:
        # Preparing the affine matrix
        affine = np.zeros((4, 4))
        affine[0, 2] = 1e-3
        affine[1, 0] = -1e-3
        affine[2, 1] = -1e-3
        affine[3, 3] = 1

        # Saving the tractogram
        tractogram_path = tmp_path + "/streamlines" + uuid.uuid4().hex + ".trk"
        sapi.save_tractogram(tractogram_path, affine)
    else:
        errors.append('no experiment(s) given')

    return tractogram_path, errors


def get_template(resolution):
    mcc.resolution = resolution # [10. 25. 50. 100]

    template = mcc.get_template_volume(file_name=model_path + "/average_template_" +
                                       str(mcc.resolution) + ".nrrd")[0]

    return nrrd_to_nifti(template, mcc.resolution)


def validate_structures(structures, errors, category):
    if structures is not None:
        for i in range(0, len(structures)):
            exist = True
            struct = structures[i]
            if struct.isdigit():
                struct = int(struct)
                structures[i] = struct
                if struct not in dict_struct_name_id:
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

    validate_structures(structures=structures,
                        errors=errors,
                        category="structure")

    validate_structures(structures=injection_structures,
                        errors=errors,
                        category="injection structures")

    validate_hemisphere(hemisphere=hemisphere,
                        errors=errors,
                        category="hemisphere")

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

    validate_structures(structures=injection_structures,
                        errors=errors,
                        category="injection structures")

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

    validate_structures(structures=injection_structures,
                        errors=errors,
                        category="injection structures")

    validate_structures(structures=target_domain,
                        errors=errors,
                        category="target domain")

    validate_structures(structures=injection_domain,
                        errors=errors,
                        category="injection domain")

    validate_hemisphere(hemisphere=injection_hemisphere,
                        errors=errors,
                        category="injection hemisphere")

    validate_hemisphere(hemisphere=target_hemisphere,
                        errors=errors,
                        category="target hemisphere")

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
            if struct in dict_struct_name_id:
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
                structures_id.extend(struct for struct in structure_childs
                                     if struct not in structures_id)
            elif depth == 'all':
                structure_descendants = st_tree.descendant_ids([structure_id])[0]
                structures_id.extend(struct for struct in structure_descendants
                                     if struct not in structures_id)

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

    return dict_proj_crossing,\
           matrix,\
           list(pm['rows']),\
           [c['label'] for c in pm['columns']],\
           errors

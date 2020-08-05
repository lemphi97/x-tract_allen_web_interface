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
import pathlib

mcc = MouseConnectivityCache()
mca = MouseConnectivityApi()
st_tree = mcc.get_structure_tree()
image_api = ImageDownloadApi()
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
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
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
                st_dict[struct_id] = struct_dict['name'] + " (" + struct_dict['acronym'] + ")"

    return st_dict

def get_all_exp():
    cre_neg_exp = mcc.get_experiments(dataframe=True, cre=False)
    cre_neg_exp['cre'] = np.zeros((len(cre_neg_exp), 1), dtype=bool)

    cre_pos_exp = mcc.get_experiments(dataframe=True, cre=True)
    cre_pos_exp['cre'] = np.ones((len(cre_pos_exp), 1), dtype=bool)

    return pd.concat([cre_neg_exp, cre_pos_exp])

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

def correlation_search(row,                          # Integer
                       structures=None,              # [String], None
                       product_ids=None,             # [Integer], None
                       hemisphere=None,              # 'left', 'right', None
                       transgenic_lines=None,        # [String], None, Specify ID '0' to exclude all TransgenicLines.
                       injection_structures=None,    # [String], None
                       primary_structure_only=None,  # True, False, None
                       sort_order=None,              # 'asc', 'desc', None
                       start_row=None,               # Integer, None
                       num_rows=None):               # Integer, None
    result = None
    errors = []

    if row not in mcc.get_experiments(dataframe=True)['id']:
        errors.append("experiment |" + str(row) + "| doesn't exist")

    if structures is not None:
        for i in range(0, len(structures)):
            struct = structures[i]
            if struct.isdigit():
                struct = int(struct)
                structures[i] = struct
                if struct not in dict_struct_id:
                    errors.append("injection structure |" + str(struct) + "| doesn't exist")
            elif struct not in dict_struct_acron or struct not in dict_struct_name:
                errors.append("structure |" + str(struct) + "| doesn't exist")

    if injection_structures is not None:
        for i in range(0, len(injection_structures)):
            struct = injection_structures[i]
            if struct.isdigit():
                struct = int(struct)
                injection_structures[i] = struct
                if struct not in dict_struct_id:
                    errors.append("injection structure |" + str(struct) + "| doesn't exist")
            elif struct not in dict_struct_acron or struct not in dict_struct_name:
                errors.append("injection structure |" + str(struct) + "| doesn't exist")

    if hemisphere is not None:
        hemisphere = hemisphere.lower()
    if hemisphere not in ["left", "right", None]:
        errors.append("hemisphere |" + str(hemisphere) + "| is invalid")

    # I don't know how to validate product id beforehand
    # I don't know how to validate transgenic line beforehand
    if transgenic_lines is not None:
        for i in range(0, len(transgenic_lines)):
            line = transgenic_lines[i]
            if line.isdigit():
                transgenic_lines[i] = line

    if len(errors) == 0:
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

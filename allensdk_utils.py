# This file is for handling Interactions with allensdk

# imports:
from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache
from allensdk.api.queries.image_download_api import ImageDownloadApi
from allensdk.api.queries.ontologies_api import OntologiesApi

import pandas as pd
from allensdk.api.queries import grid_data_api
import numpy as np
import pathlib
import nrrd

mcc = MouseConnectivityCache()
st_tree = mcc.get_structure_tree()

# return all structure in a dict (key: id, value: name with acronym)
def get_struct_in_dict(experiences):
    st_dict = {}

    for i in range(0, len(experiences)):
        index_val = experiences.iloc[i]
        struct_id = index_val['structure_id']

        if struct_id not in st_dict:
            struct_name = index_val['structure_name']
            struct_acron = index_val['structure_abbrev']
            st_dict[struct_id] = struct_name + " (" + struct_acron + ")"

        struct_p_i_s = index_val['primary_injection_structure']
        if struct_p_i_s != struct_id and struct_p_i_s not in st_dict:
            struct_dict = st_tree.get_structures_by_id([struct_p_i_s])[0]
            st_dict[struct_p_i_s] = struct_dict['name'] + " (" + struct_dict['acronym'] + ")"

    return st_dict

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

def get_all_exp():
    cre_neg_exp = mcc.get_experiments(dataframe=True, cre=False)
    cre_neg_exp['cre'] = np.zeros((len(cre_neg_exp), 1), dtype=bool)

    cre_pos_exp = mcc.get_experiments(dataframe=True, cre=True)
    cre_pos_exp['cre'] = np.ones((len(cre_pos_exp), 1), dtype=bool)

    return pd.concat([cre_neg_exp, cre_pos_exp])
# This file is for handling Interactions with allensdk

from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache
from allensdk.api.queries.image_download_api import ImageDownloadApi
from allensdk.api.queries.ontologies_api import OntologiesApi


# return all id in an array
def get_all_id(experiences):
    all_id = []
    # This loop can iterate over all our experiments
    for i in range(0, len(experiences)):
        all_id.append(experiences.iloc[i]['id'])
    return all_id

# return all structure in a dict (key: id, value: name with acronym)
def get_struct_in_dict(experiences, st_tree):
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

mcc = MouseConnectivityCache()

all_exp = mcc.get_experiments(dataframe=True)
nb_exp = len(all_exp)

st_tree = mcc.get_structure_tree()
st_dict = get_struct_in_dict(all_exp, st_tree)
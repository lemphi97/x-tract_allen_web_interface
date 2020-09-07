#!/usr/bin/env python3

"""Adapted from : https://github.com/BrancoLab/BrainRender"""

import numpy as np
from tqdm import tqdm
import pandas as pd
import requests
import nibabel as nib
from pathlib import Path


class StreamLines(object):
    def __init__(self, directory="./streamlines"):
        self.template_streamline_json_url = "https://neuroinformatics.nl/HBP/allen-connectivity-viewer/json/streamlines_{:d}.json.gz" # We are using the streamlines cache from neuroinformatics.nl
        self.data = []
        self.files = []
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def download(self, experiment_ids, force=False):
        """Downloads the streamline files for a list of experiment IDs.

        :param experiment_ids: list of integers corresponding to experiment IDs
        :param force: bool to force download, otherwise we will check the cache first.
        """

        if not isinstance(experiment_ids, (list, np.ndarray, tuple)):
            experiment_ids = [experiment_ids]

        for eid in tqdm(experiment_ids):
            url = self.make_streamline_request_url(eid)
            jsonpath = self.directory / f"{eid}.json"
            self.files.append(jsonpath)
            if not jsonpath.is_file() or force:
                response = requests.get(url)

                # Write the response content as a temporary compressed file
                temp_path = self.directory / "tmp.gz"
                with open(temp_path, "wb") as temp:
                    temp.write(response.content)

                # Open in pandas and delete temp
                url_data = pd.read_json(temp_path, lines=True, compression='gzip')
                temp_path.unlink() # Remove this file

                # save json
                url_data.to_json(jsonpath)

                # append to lists and return
                self.data.append(url_data)
            else:
                self.data.append(pd.read_json(jsonpath))

        # Updating the streamlines information
        self.n_experiments = len(self.data)
        self.n_streamlines_per_experiments = []
        for iExp in range(self.n_experiments):
            self.n_streamlines_per_experiments.append(len(self.data[iExp].lines[0]))

        # Convert the streamlines to a list of ndarrays
        # 1st dim is the number of points, 2nd dim is the xyz position
        s = []
        for iExp in range(self.n_experiments):
            for iStream in range(self.n_streamlines_per_experiments[iExp]):
                streamline = self.data[iExp].lines[0][iStream]

                n_positions = len(streamline)
                this_streamline = np.zeros((n_positions, 3), dtype=np.float32)
                for j in range(n_positions):
                    this_streamline[j, 0] = streamline[j]['x']
                    this_streamline[j, 1] = streamline[j]['y']
                    this_streamline[j, 2] = streamline[j]['z']

                s.append(this_streamline)

        self.streamlines_list = s

    def print_info(self):
        """Print some informations about the downloaded streamlines"""
        print("Number of experiments:", self.n_experiments)
        print("Number of streamlines per experiments")
        for i, n_streamlines in enumerate(self.n_streamlines_per_experiments):
            print(f"  Experiment {i} has {n_streamlines} streamlines")

    def make_streamline_request_url(self, experiment_id):
        """Get url of JSON file for an experiment
        :param experiment_id: int corresponding to an experiment ID number
        :returns str url_request
        """
        return self.template_streamline_json_url.format(experiment_id)

    def save_tractogram(self, filename, affine):
        """Save the streamlines as a tractogram using nibabel
        :param filename: str Full path to the trk filename where the tractogram should be saved
        :param affine: ndarray A 4x4 matrix describing the affine transformation to position the streamlines in the RAS+ CCF.
        """
        filename = Path(filename)
        assert filename.suffix == ".trk", "The filename must be ending with .trk"
        filename.parent.mkdir(parents=True, exist_ok=True)

        tractogram = nib.streamlines.Tractogram(self.streamlines_list, affine_to_rasmm=affine)
        nib.streamlines.save(tractogram, str(filename))

    def remove_cache(self):
        """Remove the streamlines cache"""
        for f in self.files:
            f.unlink()
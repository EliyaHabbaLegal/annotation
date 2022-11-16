import os
import re

import docx
import numpy as np
# from PIL import Image
import pandas as pd

class TxtDirManager:
    def __init__(self, dir_name):
        self._dir_name = dir_name
        self._files = []
        self._annotations_files = []

    def get_df(self, allow_types=["docx"]):
        df = pd.read_csv(r'all_results_with_origin_sen_clean.csv')
        return df

        allow_types += [i.upper() for i in allow_types]
        mask = ".*\.[" + "|".join(allow_types) + "]"
        self._files = [
            file for file in os.listdir(self._dir_name) if re.match(mask, file)
        ]
        return self._files

    def get_exist_annotation_files(self):
        self._annotations_files = [
            file for file in os.listdir(self._dir_name) if re.match(".*.xml", file)
        ]
        return self._annotations_files

    def set_all_files(self, files):
        self._files = files

    def set_annotation_files(self, files):
        self._annotations_files = files

    def get_image(self, index):
        return self._files[index]

    def _get_next_txt_helper(self, index):
        while index < len(self._files) - 1:
            index += 1
            txt_file = self._files[index]
            txt_file_name = txt_file.split(".")[0]
            if f"{txt_file_name}.xml" not in self._annotations_files:
                return index
        return None

    def get_next_annotation_txt(self, index):
        txt_index = self._get_next_txt_helper(index)
        if txt_index:
            return txt_index
        if not txt_index and len(self._files) != len(self._annotations_files):
            return self._get_next_txt_helper(0)

    def save_annotation(self, label, tagger, sentence_id):
        # read the df of the current tagger and save the label to the df
        tagger_df = pd.read_csv(os.path.join("taggers", f"{tagger}.csv"))
        tagger_df.loc[tagger_df["sentence_id"] == sentence_id, "label"] = label
        tagger_df.loc[tagger_df["sentence_id"] == sentence_id, "status"] = "annotated"

        tagger_df.to_csv(os.path.join("taggers", f"{tagger}.csv"), index=False)

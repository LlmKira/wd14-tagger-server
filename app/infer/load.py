# -*- coding: utf-8 -*-
# @Time    : 2023/12/14 下午10:20
# @Author  : sudoskys
# @File    : load.py
# @Software: PyCharm
import os
from typing import Tuple

import numpy as np
import onnxruntime as ort
import pandas as pd
from onnxruntime import InferenceSession

from .error import LoadError


def singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


def load_labels(
    label_csv_path: str,
) -> Tuple:
    """
    Load labels from csv
    :param label_csv_path: csv path
    :return: tag_names, rating_indexes, general_indexes, character_indexes
    :raises: LoadError
    """
    assert isinstance(label_csv_path, str), "label_csv_path must be a str"
    if os.path.exists(label_csv_path) is False:
        raise LoadError("label csv path not exists")
    if not label_csv_path.endswith(".csv"):
        raise LoadError("label csv path must end with .csv")
    if not os.path.isfile(label_csv_path):
        raise LoadError("label csv path must be a file")
    df = pd.read_csv(label_csv_path)
    tag_names = df["name"].tolist()
    rating_indexes = list(np.where(df["category"] == 9)[0])
    general_indexes = list(np.where(df["category"] == 0)[0])
    character_indexes = list(np.where(df["category"] == 4)[0])
    return tag_names, rating_indexes, general_indexes, character_indexes


class RuntimeManager(object):
    def __init__(self):
        self._cached_runtime = {}

    def get_runtime(self, model_path: str):
        """
        get onnxruntime from cache or create a new one
        :param model_path:
        :return:
        """
        if os.path.exists(model_path) is False:
            raise LoadError("model path not exists")
        if not model_path.endswith(".onnx"):
            raise LoadError("model path must end with .onnx")
        if model_path in self._cached_runtime:
            return self._cached_runtime[model_path]
        model = InferenceSession(model_path, providers=ort.get_available_providers())
        self._cached_runtime[model_path] = model
        return model


OnnxRuntimeManager = RuntimeManager()

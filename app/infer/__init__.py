# -*- coding: utf-8 -*-
# @Time    : 2023/12/14 下午7:44
# @Author  : sudoskys
# @File    : __init__.py.py
# @Software: PyCharm
import asyncio
from typing import Tuple

import PIL
import cv2
import numpy as np
from PIL import Image
from loguru import logger

from .load import OnnxRuntimeManager, load_labels, singleton
from .setup import download_csv, download_model


# import nest_asyncio
# nest_asyncio.apply()


def make_square(img, target_size):
    old_size = img.shape[:2]
    desired_size = max(old_size)
    desired_size = max(desired_size, target_size)

    delta_w = desired_size - old_size[1]
    delta_h = desired_size - old_size[0]
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)

    color = [255, 255, 255]
    new_im = cv2.copyMakeBorder(
        img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
    )
    return new_im


def smart_resize(img, size):
    # Assumes the image has already gone through make_square
    if img.shape[0] > size:
        img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
    elif img.shape[0] < size:
        img = cv2.resize(img, (size, size), interpolation=cv2.INTER_CUBIC)
    return img


async def infer_tag(
    image: Image.Image,
    model_path: str,
    tag_names: list[str],
    rating_indexes: list[np.int64],
    general_indexes: list[np.int64],
    character_indexes: list[np.int64],
    general_threshold: float = 0.35,
    character_threshold: float = 0.85,
) -> Tuple:
    """
    Tag Picture
    :param image: 图片

    :param model_path: 模型路径

    :param general_threshold: 一般标签阈值
    :param character_threshold: 人物标签阈值

    :param tag_names: 标签名
    :param rating_indexes: 评级索引
    :param general_indexes: 一般标签索引
    :param character_indexes: 人物标签索引

    :return: (Processed, Original, Rating, Characters, General)
    :raises: LoadError
    """
    model = OnnxRuntimeManager.get_runtime(model_path=model_path)
    _, height, width, _ = model.get_inputs()[0].shape

    # Alpha to white
    image = image.convert("RGBA")
    new_image = PIL.Image.new("RGBA", image.size, "WHITE")
    new_image.paste(image, mask=image)
    image = new_image.convert("RGB")
    image = np.asarray(image)

    # PIL RGB to OpenCV BGR
    image = image[:, :, ::-1]

    image = make_square(image, height)
    image = smart_resize(image, height)
    image = image.astype(np.float32)
    image = np.expand_dims(image, 0)

    input_name = model.get_inputs()[0].name
    label_name = model.get_outputs()[0].name
    probs = model.run([label_name], {input_name: image})[0]

    labels = list(zip(tag_names, probs[0].astype(float)))

    # First 4 labels are actually ratings: pick one with argmax
    ratings_names = [labels[i] for i in rating_indexes]
    rating = dict(ratings_names)

    # Then we have general tags: pick anywhere prediction confidence > threshold
    general_names = [labels[i] for i in general_indexes]
    general_res = [x for x in general_names if x[1] > general_threshold]
    general_res = dict(general_res)

    # Everything else is characters: pick anywhere prediction confidence > threshold
    character_names = [labels[i] for i in character_indexes]
    character_res = [x for x in character_names if x[1] > character_threshold]
    character_res = dict(character_res)

    bon_tags = dict(sorted(general_res.items(), key=lambda item: item[1], reverse=True))
    tag_result = (
        ", ".join(list(bon_tags.keys()))
        .replace("_", " ")
        .replace("(", r"\(")
        .replace(")", r"\)")
    )  # Processed
    origin_result = ", ".join(list(bon_tags.keys()))  # Original

    logger.info(f"Tagged {image.size} image with {len(bon_tags)} tags")
    logger.debug(f"Tags: {tag_result}")
    return tag_result, origin_result, rating, character_res, general_res


@singleton
class InferClient(object):
    def __init__(self, model_name: str, model_dir: str = "models"):
        self.model_path = None
        self.tag_csv_path = None

        self.tag_names = None
        self.rating_indexes = None
        self.general_indexes = None
        self.character_indexes = None

        self.set_up(model_name=model_name, model_dir=model_dir)

    def set_up(self, model_name: str, model_dir: str):
        # Download model and csv
        def sync(coro):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(coro)

        logger.info("Setting up inference client...")

        model_path = sync(download_model(model_name, file_dir=model_dir))
        tag_csv_path = sync(download_csv(model_name, file_dir=model_dir))
        self.model_path = model_path
        self.tag_csv_path = tag_csv_path

        # Load labels
        tag_names, rating_indexes, general_indexes, character_indexes = load_labels(
            self.tag_csv_path
        )
        self.tag_names = tag_names
        self.rating_indexes = rating_indexes
        self.general_indexes = general_indexes
        self.character_indexes = character_indexes
        return self

    async def infer(
        self,
        image: Image.Image,
        general_threshold: float = 0.35,
        character_threshold: float = 0.85,
    ):
        # Infer tag
        return await infer_tag(
            image=image,
            model_path=self.model_path,
            general_threshold=general_threshold,
            character_threshold=character_threshold,
            tag_names=self.tag_names,
            rating_indexes=self.rating_indexes,
            general_indexes=self.general_indexes,
            character_indexes=self.character_indexes,
        )

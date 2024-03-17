# -*- coding: utf-8 -*-
# @Time    : 2023/12/14 下午7:44
# @Author  : sudoskys
# @File    : __init__.py

import asyncio
import pathlib
import numpy as np
from PIL import Image
from loguru import logger

from .load import OnnxRuntimeManager, load_labels, singleton, mcut_threshold
from .setup import download_csv, download_model


# import nest_asyncio
# nest_asyncio.apply()
class Predictor(object):
    def __init__(
        self,
        model,
        model_target_size,
        tag_names,
        rating_indexes,
        general_indexes,
        character_indexes,
    ):
        self.model = model
        self.model_target_size = model_target_size
        self.tag_names = tag_names
        self.rating_indexes = rating_indexes
        self.general_indexes = general_indexes
        self.character_indexes = character_indexes

    def prepare_image(self, image):
        target_size = self.model_target_size

        # Convert to RGBA
        image = image.convert("RGBA")

        canvas = Image.new("RGBA", image.size, (255, 255, 255))
        canvas.alpha_composite(image)
        image = canvas.convert("RGB")

        # Pad image to square
        image_shape = image.size
        max_dim = max(image_shape)
        pad_left = (max_dim - image_shape[0]) // 2
        pad_top = (max_dim - image_shape[1]) // 2

        padded_image = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
        padded_image.paste(image, (pad_left, pad_top))

        # Resize
        if max_dim != target_size:
            padded_image = padded_image.resize(
                (target_size, target_size),
                Image.BICUBIC,
            )

        # Convert to numpy array
        image_array = np.asarray(padded_image, dtype=np.float32)

        # Convert PIL-native RGB to BGR
        image_array = image_array[:, :, ::-1]

        return np.expand_dims(image_array, axis=0)

    def predict(
        self,
        image: Image.Image,
        general_thresh: float,
        general_mcut_enabled: bool,
        character_thresh: float,
        character_mcut_enabled: bool,
    ):
        image = self.prepare_image(image)

        input_name = self.model.get_inputs()[0].name
        label_name = self.model.get_outputs()[0].name
        preds = self.model.run([label_name], {input_name: image})[0]

        labels = list(zip(self.tag_names, preds[0].astype(float)))

        # First 4 labels are actually ratings: pick one with argmax
        ratings_names = [labels[i] for i in self.rating_indexes]
        rating = dict(ratings_names)

        # Then we have general tags: pick anywhere prediction confidence > threshold
        general_names = [labels[i] for i in self.general_indexes]

        if general_mcut_enabled:
            general_probs = np.array([x[1] for x in general_names])
            general_thresh = mcut_threshold(general_probs)

        general_res = [x for x in general_names if x[1] > general_thresh]
        general_res = dict(general_res)

        # Everything else is characters: pick anywhere prediction confidence > threshold
        character_names = [labels[i] for i in self.character_indexes]

        if character_mcut_enabled:
            character_probs = np.array([x[1] for x in character_names])
            character_thresh = mcut_threshold(character_probs)
            character_thresh = max(0.15, character_thresh)

        character_res = [x for x in character_names if x[1] > character_thresh]
        character_res = dict(character_res)

        sorted_general_strings = sorted(
            general_res.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        sorted_general_strings = [x[0] for x in sorted_general_strings]
        sorted_general_strings = (
            ", ".join(sorted_general_strings).replace("(", "\(").replace(")", "\)")
        )

        return sorted_general_strings, rating, character_res, general_res


@singleton
class InferClient(object):
    def __init__(
        self,
        model_name: str,
        model_dir: str = "models",
        skip_auto_download: bool = False,
    ):
        self.model_path = None
        self.tag_csv_path = None

        self.tag_names = None
        self.rating_indexes = None
        self.general_indexes = None
        self.character_indexes = None

        self.set_up(
            model_name=model_name,
            model_dir=model_dir,
            skip_auto_download=skip_auto_download,
        )

    def set_up(self, model_name: str, model_dir: str, skip_auto_download: bool = False):
        # Download model and csv
        def sync(coro):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(coro)

        logger.info("Setting up inference client...")
        if skip_auto_download:
            logger.warning("Skipping auto download")
            model_path = (
                pathlib.Path(model_dir).joinpath(f"{model_name}.onnx").absolute()
            )
            tag_csv_path = (
                pathlib.Path(model_dir).joinpath(f"{model_name}.csv").absolute()
            )
            if not model_path.exists():
                raise FileNotFoundError(f"Model {model_name} not exists")
            if not tag_csv_path.exists():
                raise FileNotFoundError(f"Tagger CSV {model_name} not exists")
            self.model_path = str(model_path)
            self.tag_csv_path = str(tag_csv_path)
        else:
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
        character_mcut_enabled: bool = True,
        general_mcut_enabled: bool = True,
    ) -> tuple:
        model = OnnxRuntimeManager.get_runtime(model_path=self.model_path)
        _, model_target_size, width, _ = model.get_inputs()[0].shape
        # Infer tag
        predictor = Predictor(
            model=model,
            model_target_size=model_target_size,
            tag_names=self.tag_names,
            rating_indexes=self.rating_indexes,
            general_indexes=self.general_indexes,
            character_indexes=self.character_indexes,
        )
        return predictor.predict(
            image=image,
            general_thresh=general_threshold,
            general_mcut_enabled=general_mcut_enabled,
            character_thresh=character_threshold,
            character_mcut_enabled=character_mcut_enabled,
        )

# -*- coding: utf-8 -*-
# @Time    : 2023/12/14 下午7:58
# @Author  : sudoskys
# @File    : settings.py
# @Software: PyCharm
import pathlib

from dotenv import load_dotenv
from loguru import logger
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .values import all_wd_models

load_dotenv()


class InferSetting(BaseSettings):
    wd_model_name: str = "wd-swinv2-tagger-v3"
    wd_model_dir: str = "models"
    skip_auto_download: bool = False

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @model_validator(mode="after")
    def check_setting(self):
        if self.wd_model_name not in all_wd_models:
            raise ValueError(f"model_name must be in {all_wd_models}")
        if "/" in self.wd_model_name:
            raise ValueError("model_name must not contain '/'")
        if "\\" in self.wd_model_name:
            raise ValueError("model_name must not contain '\\'")
        model_dir_obj = pathlib.Path(self.wd_model_dir)
        if not model_dir_obj.exists():
            logger.warning(f"model_dir {self.wd_model_dir} not exists,will create it")
            model_dir_obj.mkdir(parents=True, exist_ok=True)
            logger.success(f"model_dir {model_dir_obj.absolute()} created")
        if not model_dir_obj.is_dir():
            raise ValueError(f"model_dir {self.wd_model_dir} is not a dir")
        return self

    @property
    def model_path(self):
        model_dir_obj = pathlib.Path(self.wd_model_dir)
        model_path = model_dir_obj.joinpath(self.wd_model_name + ".onnx")
        return model_path


InferSettingCurrent = InferSetting()

# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 上午12:21
# @Author  : sudoskys
# @File    : main.py
# @Software: PyCharm
import sys

import uvicorn
from dotenv import load_dotenv
from loguru import logger
from pydantic import model_validator
from pydantic_settings import BaseSettings

import app

load_dotenv()
logger.remove()
logger.add(sys.stderr, level="INFO", colorize=True, enqueue=True)
logger.add(
    sink="run.log",
    format="{time} - {level} - {message}",
    level="INFO",
    rotation="100 MB",
    enqueue=True,
)


class ServerSetting(BaseSettings):
    server_port: int = 10010
    server_host: str = "127.0.0.1"

    @model_validator(mode="after")
    def check(self):
        if self.server_host.startswith("https://"):
            self.server_host = self.server_host.replace("https://", "")
            logger.warning("Wrong HOST, should remove the prefix https://")
        if self.server_host.startswith("http://"):
            self.server_host = self.server_host.replace("http://", "")
            logger.warning("Wrong HOST, should remove the prefix http://")
        assert isinstance(self.server_host, str)
        assert isinstance(self.server_port, int)
        return self


setting = ServerSetting()
logger.info(f"Docs: http://{setting.server_host}:{setting.server_port}/docs")
uvicorn.run(app.app, host=setting.server_host, port=setting.server_port)

# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 上午12:21
# @Author  : sudoskys
# @File    : main.py
# @Software: PyCharm
import os
import sys

import uvicorn
from dotenv import load_dotenv
from loguru import logger

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
server_port = os.getenv("PORT", 8889)
server_host = os.getenv("HOST", "127.0.0.1")
logger.info(f"Running on {server_host}:{server_port}")
if server_host.startswith("https://"):
    server_host = server_host.replace("https://", "")
    logger.warning("Wrong HOST, should remove the prefix https://")
if server_host.startswith("http://"):
    server_host = server_host.replace("http://", "")
    logger.warning("Wrong HOST, should remove the prefix http://")
assert isinstance(server_host, str)
assert isinstance(server_port, int)
uvicorn.run(app.app, host=server_host, port=server_port)

# -*- coding: utf-8 -*-
# @Time    : 2023/12/14 下午11:58
# @Author  : sudoskys
# @File    : test_app.py
# @Software: PyCharm
# test_app.py
import pytest
from sanic_testing.testing import SanicTestClient

from app import app


@pytest.fixture
def test_cli(loop):
    return SanicTestClient(app, loop)


@pytest.mark.asyncio
async def test_upload(test_cli):
    # Replace with your actual file and token
    data = {
        "file": open("test_src_01.png", "rb"),
        "token": "your_token",
        "general_threshold": "0.35",
        "character_threshold": "0.85",
    }
    response = await test_cli.post("/upload", data=data)
    assert response.status == 200

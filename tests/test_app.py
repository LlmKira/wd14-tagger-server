# -*- coding: utf-8 -*-
# @Time    : 2023/12/14 下午11:58
# @Author  : sudoskys
# @File    : test_app.py
# @Software: PyCharm

import pytest
from fastapi.testclient import TestClient

from app import app


@pytest.fixture
def test_cli():
    return TestClient(app)


@pytest.mark.asyncio
async def test_upload(test_cli):
    # Replace with your actual file and token
    data = {
        "file": ("test_src_01.png", open("test_src_01.png", "rb")),
        "token": "your_token",
        "general_threshold": "0.35",
        "character_threshold": "0.85",
    }
    response = test_cli.post("/upload", files=data)
    assert response.status_code == 200

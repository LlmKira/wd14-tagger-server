# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 上午12:00
# @Author  : sudoskys
# @File    : sdk.py
# @Software: PyCharm
import aiofiles
import aiohttp


class WdTaggerSDK:
    def __init__(self, base_url):
        self.base_url = base_url

    async def upload(
        self, file_path, token, general_threshold=0.35, character_threshold=0.85
    ):
        url = f"{self.base_url}/upload"
        async with aiofiles.open(file_path, "rb") as f:
            file = await f.read()
        data = {
            "file": file,
            "token": token,
            "general_threshold": str(general_threshold),
            "character_threshold": str(character_threshold),
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                return await response.json()

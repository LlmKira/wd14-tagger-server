# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 上午12:21
# @Author  : sudoskys
# @File    : main.py
# @Software: PyCharm


import uvicorn

import app

uvicorn.run(app.app, host="127.0.0.1", port=8888)

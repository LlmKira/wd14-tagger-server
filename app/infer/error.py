# -*- coding: utf-8 -*-
# @Time    : 2023/12/14 下午11:26
# @Author  : sudoskys
# @File    : error.py
# @Software: PyCharm
class LoadError(Exception):
    pass


class DownloadError(Exception):
    pass


class FileSizeMismatchError(Exception):
    pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/11/9 下午7:21
# @Author  : Heshouyi
# @File    : file_path.py
# @Software: PyCharm
# @description:

import os

'''后端目录'''
# 后端根目录，指向langchain_project/backend
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

'''一级目录'''
log_path = os.path.abspath(os.path.join(project_path, 'logs'))      # 日志目录


if __name__ == '__main__':
    from .logger import logger
    logger.info(f"项目路径: {project_path}")

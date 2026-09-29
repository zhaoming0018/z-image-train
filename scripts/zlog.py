#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一日志配置（loguru）——脚本的「进度/事件/诊断」走 stderr（TTY 带色，非 TTY 纯文本）。

约定：
- 数据产出（被解析/被捕获的单行结果、JSON、摘要报告）仍走 stdout（print），不要混入日志。
- 级别可用环境变量 ZLOG_LEVEL 覆盖，如 `ZLOG_LEVEL=DEBUG python3 xxx.py`。
用法:
    from zlog import logger, setup_logging
    setup_logging()
    logger.info("...")
"""
import os
import sys

from loguru import logger

__all__ = ["logger", "setup_logging"]

_FORMAT = ("<dim>{time:MM-DD HH:mm:ss}</dim> | <level>{level: <7}</level> | "
           "<level>{message}</level>")


def setup_logging(level=None):
    """重置 loguru 全局 sink：单 stderr 输出。level 缺省取 ZLOG_LEVEL / INFO。"""
    level = (level or os.environ.get("ZLOG_LEVEL") or "INFO").upper()
    logger.remove()
    logger.add(sys.stderr, format=_FORMAT, level=level)
    return logger

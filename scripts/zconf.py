#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""z-image-train 仓库路径与配置加载公共库（配置统一放 <repo>/config/）。

约定：脚本一律从这里取 ROOT / CONFIG_DIR，不要再各自 os.path.dirname(__file__) 或硬编码家目录。
用法:
    from zconf import ROOT, CONFIG_DIR, load_yaml, load_specs
"""
import os
from glob import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(ROOT, "config")


def load_yaml(path):
    """读一个 YAML 文件；缺 pyyaml 时给出可操作报错（系统 /usr/bin/python3 已带）。"""
    try:
        import yaml
    except ImportError:
        raise SystemExit("缺少 yaml：请用 /usr/bin/python3 运行（系统 python3 已带 pyyaml）")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_specs(subdir):
    """config/<subdir>/*.yaml → {slug: doc}（按文件名排序，保证稳定）。"""
    specs = {}
    for path in sorted(glob(os.path.join(CONFIG_DIR, subdir, "*.yaml"))):
        specs[os.path.splitext(os.path.basename(path))[0]] = load_yaml(path)
    return specs

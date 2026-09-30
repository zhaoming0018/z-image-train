#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从定妆候选构建训练数据集（代码与数据分离：选择清单在 config/datasets/<slug>.yaml）。
用法（CLI 基于 typer）: python3 scripts/build_dataset.py [slug ...] [--force]   （幂等：已有文件跳过；--force 覆盖）
输出：datasets/<slug>/ds_<slug>_NN.png|.txt；caption = "<appearance>, <pose>"（短句，逗号分隔），风格对齐 l6liu/he6tou。
"""
import os
import shutil
from typing import Annotated, Optional

import typer

from zconf import ROOT, load_specs
from zlog import logger, setup_logging

AUD = os.path.join(ROOT, "output/liulaoliu_story/audition")
DST = os.path.join(ROOT, "datasets")

app = typer.Typer(add_completion=False, help="定妆候选 → 训练数据集构建（规格来自 config/datasets/*.yaml）")


def build(tag, spec, force=False):
    d = os.path.join(DST, tag)
    os.makedirs(d, exist_ok=True)
    picks = spec["picks"]
    n, miss = 0, []
    for i, p in enumerate(picks, 1):
        s = os.path.join(AUD, spec["audition_dir"], p["src"])
        if not os.path.exists(s):
            miss.append(p["src"]); continue
        base = f"ds_{tag}_{i:02d}"
        png, txt = os.path.join(d, base + ".png"), os.path.join(d, base + ".txt")
        if os.path.exists(png) and os.path.exists(txt) and not force:
            n += 1; continue
        shutil.copyfile(s, png)
        with open(txt, "w", encoding="utf-8") as f:
            f.write(f"{spec['appearance']}, {p['pose']}\n")
        n += 1
    logger.info(f"[{tag}] {n}/{len(picks)} 张就绪")
    if miss:
        logger.warning(f"[{tag}] ⚠️ 缺失源图: {miss}")
    return len(miss)


@app.command()
def main(
    slugs: Annotated[Optional[list[str]], typer.Argument(help="slug（如 fu6lao）；缺省=config/datasets/ 全部")] = None,
    force: Annotated[bool, typer.Option("--force", help="已存在文件也重新覆盖")] = False,
):
    """把定妆候选按 config/datasets/<slug>.yaml 规格拷成训练数据集（ds_<slug>_NN.png/.txt）。"""
    setup_logging()
    specs = load_specs("datasets")
    miss_total = 0
    for tag in slugs or sorted(specs):
        if tag not in specs:
            logger.warning(f"未知规格: {tag}")
            continue
        miss_total += build(tag, specs[tag], force)
    logger.success("BUILD DONE" + (f" (缺失 {miss_total})" if miss_total else ""))


if __name__ == "__main__":
    app()

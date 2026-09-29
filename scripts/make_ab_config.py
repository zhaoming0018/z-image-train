#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 l6liu_zimage.yaml 生成 A/B 实验配置（文本手术 + 断言防呆）
用法（CLI 基于 typer）:
  python3 make_ab_config.py --out ~/z-image-train/config/train/ab/ab_e1.yaml --name ab_e1_resident --steps 60 --resident
"""
import os
import re
from typing import Annotated

import typer

from zlog import logger, setup_logging

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "config", "train", "l6liu_zimage.yaml")

app = typer.Typer(add_completion=False, help="A/B 实验配置生成器")


def sub1(text, old, new, tag):
    n = text.count(old)
    if n != 1:
        logger.error(f"FATAL: pattern[{tag}] found {n} times, expected 1")
        raise typer.Exit(2)
    return text.replace(old, new)


@app.command()
def main(
    out: Annotated[str, typer.Option("--out", help="输出 yaml 路径")],
    name: Annotated[str, typer.Option("--name", help="实验名（写入 name 字段）")],
    steps: Annotated[int, typer.Option("--steps", help="训练步数")],
    resident: Annotated[bool, typer.Option("--resident", help="low_vram=false + layer_offloading=false")] = False,
    nockpt: Annotated[bool, typer.Option("--nockpt", help="gradient_checkpointing=false")] = False,
    res768: Annotated[bool, typer.Option("--res768", help="resolution [768] only")] = False,
    batch: Annotated[int, typer.Option("--batch", help="batch_size")] = 1,
):
    """生成实验配置（文本替换 + 断言每处恰好命中 1 次）。"""
    setup_logging()
    with open(os.path.abspath(BASE), encoding="utf-8") as f:
        t = f.read()

    t = sub1(t, '  name: "l6liu_zimage_lora_v1"', f'  name: "{name}"', "name")
    t = sub1(
        t,
        'training_folder: "/home/zhaoyiming/z-image-train/output"',
        'training_folder: "/home/zhaoyiming/z-image-train/output_ab"',
        "folder",
    )
    t = sub1(t, "save_every: 250", "save_every: 10000", "save_every")
    t = sub1(t, "steps: 2500", f"steps: {steps}", "steps")
    # 量化口径统一：显式 float8（与带适配器时实际生效的一致），避免实验间隐性差异
    t = sub1(
        t,
        'qtype: "qfloat8"',
        'qtype: "float8"\n        qtype_te: "float8"',
        "qtype",
    )
    # 实验跑完全关闭采样（省 46s/次 的样图生成）
    t = sub1(
        t,
        "        dtype: bf16\n",
        "        dtype: bf16\n        skip_first_sample: true\n        disable_sampling: true\n",
        "nosample",
    )
    if batch != 1:
        t = sub1(t, "batch_size: 1", f"batch_size: {batch}", "batch")
    if nockpt:
        t = sub1(t, "gradient_checkpointing: true", "gradient_checkpointing: false", "nockpt")
    if res768:
        t = sub1(t, "resolution: [ 768, 1024 ]", "resolution: [ 768 ]", "res768")
    if resident:
        t = sub1(t, "low_vram: true", "low_vram: false", "lowvram")
        t = sub1(t, "layer_offloading: true", "layer_offloading: false", "offload")

    out_abs = os.path.abspath(out)
    with open(out_abs, "w", encoding="utf-8") as f:
        f.write(t)
    logger.info(f"WROTE {out_abs}")
    for ln in t.splitlines():
        if re.search(
            r"name:|steps:|batch_size:|gradient_checkpointing:|low_vram:|layer_offloading:|"
            r"resolution:|save_every:|qtype|disable_sampling|skip_first|training_folder",
            ln,
        ):
            logger.info("    " + ln.strip())


if __name__ == "__main__":
    app()

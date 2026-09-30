#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""带 LoRA 的 Z-Image 出图脚本（用于训练后对比测试）
用法（CLI 基于 typer）: python3 gen_with_lora.py <输出名> <seed> <lora规格> <提示词>
  lora规格: "none" 或 "文件名:强度[,文件名2:强度2]" 例如:
    "l6liu_zimage_lora_v1.safetensors:0.9"
    "l6liu_zimage_lora_v1.safetensors:0.8,he6tou_zimage_lora_v1.safetensors:0.8"
输出: ~/.hermes/cache/scratch/<输出名>.png
日志: loguru → stderr（成功/失败信息）。ComfyUI 调用走 comfy_lib（自动绕环境代理）。
"""
from pathlib import Path
from typing import Annotated

import typer

from comfy_lib import build_workflow, render
from zconf import CONFIG_DIR
from zlog import logger, setup_logging

SCRATCH = Path.home() / ".hermes/cache/scratch"
WF = CONFIG_DIR / "z_image_api.json"

app = typer.Typer(add_completion=False, help="带 LoRA 的 Z-Image 出图（对比测试）")


def parse_loras(spec):
    """"文件名:强度[,文件2:强度2]" → [{'lora','strength'}...]；none / 空 → []。"""
    if not spec or spec == "none":
        return []
    loras = []
    for part in spec.split(","):
        name, _, st = part.partition(":")
        loras.append({"lora": name, "strength": float(st) if st else 1.0})
    return loras


@app.command()
def main(
    out_name: Annotated[str, typer.Argument(help="输出名（存到 scratch/<名>.png）")],
    seed: Annotated[int, typer.Argument(help="随机种子")],
    lora_spec: Annotated[str, typer.Argument(help='"none" 或 "文件名:强度[,文件2:强度2]"')],
    prompt: Annotated[str, typer.Argument(help="出图提示词")],
):
    """提交工作流到 ComfyUI 桥接，等待完成并拷回 scratch。"""
    setup_logging()
    wf = build_workflow(WF, prompt, seed, parse_loras(lora_spec))
    dst = SCRATCH / f"{out_name}.png"
    res = render(wf, dst, "lora-test", poll_timeout=240.0)
    if not res["ok"]:
        logger.error(res["error"])
        raise typer.Exit(2 if "轮询" in res["error"] else 1)
    logger.success(f"OK {res['seconds']:.0f}s -> {dst} ({res['size']} bytes)")


if __name__ == "__main__":
    app()

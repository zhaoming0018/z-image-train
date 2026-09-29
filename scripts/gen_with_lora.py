#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""带 LoRA 的 Z-Image 出图脚本（用于训练后对比测试）
用法（CLI 基于 typer）: python3 gen_with_lora.py <输出名> <seed> <lora规格> <提示词>
  lora规格: "none" 或 "文件名:强度[,文件名2:强度2]" 例如:
    "l6liu_zimage_lora_v1.safetensors:0.9"
    "l6liu_zimage_lora_v1.safetensors:0.8,he6tou_zimage_lora_v1.safetensors:0.8"
输出: /home/zhaoyiming/.hermes/cache/scratch/<输出名>.png
日志: loguru → stderr（成功/失败信息）
"""
import json
import os
import shutil
import time
import urllib.request
from typing import Annotated

import typer

from zlog import logger, setup_logging

BRIDGE = "http://127.0.0.1:8199"
OUT_DIR = "/mnt/d/minimax-h3-demo/ComfyUI/output"
SCRATCH = "/home/zhaoyiming/.hermes/cache/scratch"
WF = os.path.join(SCRATCH, "z_image_api.json")

app = typer.Typer(add_completion=False, help="带 LoRA 的 Z-Image 出图（对比测试）")


def req(url, data=None):
    r = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None,
                               headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())


@app.command()
def main(
    out_name: Annotated[str, typer.Argument(help="输出名（存到 scratch/<名>.png）")],
    seed: Annotated[int, typer.Argument(help="随机种子")],
    lora_spec: Annotated[str, typer.Argument(help='"none" 或 "文件名:强度[,文件2:强度2]"')],
    prompt: Annotated[str, typer.Argument(help="出图提示词")],
):
    """提交工作流到 ComfyUI 桥接，等待完成并拷回 scratch。"""
    setup_logging()
    wf = json.load(open(WF))
    wf["27"]["inputs"]["text"] = prompt
    wf["3"]["inputs"]["seed"] = seed

    if lora_spec and lora_spec != "none":
        prev = "28"
        for i, part in enumerate(lora_spec.split(",")):
            name, _, st = part.partition(":")
            st = float(st) if st else 1.0
            nid = str(40 + i)
            wf[nid] = {"class_type": "LoraLoaderModelOnly",
                       "inputs": {"model": [prev, 0], "lora_name": name, "strength_model": st}}
            prev = nid
        wf["11"]["inputs"]["model"] = [prev, 0]

    resp = req(f"{BRIDGE}/prompt", {"prompt": wf, "client_id": "lora-test"})
    pid = resp.get("prompt_id")
    if not pid:
        logger.error(f"SUBMIT FAIL: {json.dumps(resp)[:400]}")
        raise typer.Exit(1)
    t0 = time.time()
    while time.time() - t0 < 240:
        time.sleep(2)
        h = req(f"{BRIDGE}/history/{pid}")
        if pid in h and h[pid].get("outputs"):
            f0 = h[pid]["outputs"]["9"]["images"][0]
            src = os.path.join(OUT_DIR, f0.get("subfolder", ""), f0["filename"])
            dst = os.path.join(SCRATCH, f"{out_name}.png")
            shutil.copyfile(src, dst)
            logger.success(f"OK {time.time()-t0:.0f}s -> {dst} ({os.path.getsize(dst)} bytes)")
            return
    logger.error("TIMEOUT")
    raise typer.Exit(2)


if __name__ == "__main__":
    app()

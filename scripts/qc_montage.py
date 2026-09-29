#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把数据集目录里的图片拼成质检用网格图（文件名标注在上方）。
用法（CLI 基于 typer；需要 PIL → 用 aitk python 跑）: python3 qc_montage.py <图片目录> <输出png> [每行张数] [缩略图边长]
"""
import os
from typing import Annotated

import typer
from PIL import Image, ImageDraw, ImageFont

app = typer.Typer(add_completion=False, help="图片网格拼图（质检用）")


def make_montage(img_dir, out_path, cols=5, thumb=512):
    files = sorted([f for f in os.listdir(img_dir) if f.lower().endswith(".png")])
    if not files:
        print("no images")
        return
    label_h = 28
    rows = (len(files) + cols - 1) // cols
    W = cols * thumb
    H = rows * (thumb + label_h)
    canvas = Image.new("RGB", (W, H), (24, 24, 24))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    for i, fn in enumerate(files):
        r, c = divmod(i, cols)
        x, y = c * thumb, r * (thumb + label_h)
        im = Image.open(os.path.join(img_dir, fn)).convert("RGB")
        im.thumbnail((thumb, thumb))
        ox = x + (thumb - im.width) // 2
        oy = y + label_h + (thumb - im.height) // 2
        canvas.paste(im, (ox, oy))
        draw.text((x + 6, y + 3), fn, fill=(255, 220, 120), font=font)
    canvas.save(out_path)
    print(f"montage -> {out_path} ({W}x{H}, {len(files)} imgs)")


@app.command()
def main(
    img_dir: Annotated[str, typer.Argument(help="图片目录")],
    out: Annotated[str, typer.Argument(help="输出 png 路径")],
    cols: Annotated[int, typer.Argument(help="每行张数")] = 5,
    thumb: Annotated[int, typer.Argument(help="缩略图边长（px）")] = 512,
):
    """把目录内 PNG 拼成网格图。"""
    make_montage(img_dir, out, cols, thumb)


if __name__ == "__main__":
    app()

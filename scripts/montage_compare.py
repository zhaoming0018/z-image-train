#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Qwen-Image 2.1 vs Z-Image Turbo 的对比拼图。

用法：~/miniconda3/envs/aitk/bin/python3 montage_compare.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DEST = Path("/home/zhaoyiming/z-image-train/output/model_compare")
SCENES = [
    ("ch15", "s2_drive", "ch15 s2_drive — Car interior, 2 people (hardest shot)"),
    ("ch13", "s3_poster", "ch13 s3_poster — Office desk confrontation"),
    ("ch11", "s5_hug", "ch11 s5_hug — Group hug, 3 people"),
]
LABELS = [
    ("qwen", "Qwen-Image 2.1 (25 steps, int8)"),
    ("zimg", "Z-Image Turbo (8 steps, bf16)"),
]

THUMB = 640
GAP = 12
HEADER = 56
CAP = 36

fd = "/usr/share/fonts/truetype/dejavu"
f_head = ImageFont.truetype(f"{fd}/DejaVuSans-Bold.ttf", 26)
f_cap = ImageFont.truetype(f"{fd}/DejaVuSans.ttf", 22)

W = GAP + THUMB + GAP + THUMB + GAP
H = HEADER + THUMB + CAP + GAP

made = []
for chapter, scene, title in SCENES:
    canvas = Image.new("RGB", (W, H), (18, 18, 18))
    draw = ImageDraw.Draw(canvas)
    draw.text((GAP + 4, 14), title, fill=(255, 220, 120), font=f_head)
    ok = True
    for i, (model, label) in enumerate(LABELS):
        p = DEST / f"{model}_{chapter}_{scene}.png"
        if not p.exists():
            ok = False
            continue
        im = Image.open(p).convert("RGB").resize((THUMB, THUMB), Image.LANCZOS)
        x = GAP + i * (THUMB + GAP)
        canvas.paste(im, (x, HEADER))
        draw.text((x + 4, HEADER + THUMB + 6), label, fill=(200, 200, 200), font=f_cap)
    out = DEST / f"cmp_{chapter}_{scene}.png"
    canvas.save(out)
    made.append(str(out))
    print(f"{'ok' if ok else 'MISSING SOME'} -> {out}")

# 总览（3 行纵向，缩到 40%）
if len(made) == len(SCENES):
    rows = [Image.open(m) for m in made]
    scale = 0.42
    rw, rh = int(W * scale), int(H * scale)
    total = Image.new("RGB", (rw, rh * len(rows) + 20 * (len(rows) - 1)), (30, 30, 30))
    y = 0
    for r in rows:
        total.paste(r.resize((rw, rh), Image.LANCZOS), (0, y))
        y += rh + 20
    ov = DEST / "cmp_overview.png"
    total.save(ov)
    print(f"overview -> {ov} ({total.width}x{total.height})")
print("DONE")

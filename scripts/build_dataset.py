#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从定妆候选构建训练数据集：fu6lao / huiming / houshaolin（侯少麟）/ tongyuhui（佟御辉）。
选择依据：视觉质检 + 用户拍板（2026-09-29：慧铭=无眼镜版；富老大、侯少麟、佟御辉均已通过）。
用途（CLI 基于 typer）: python3 scripts/build_dataset.py [--force]   （幂等：已有文件跳过；--force 覆盖）
输出：datasets/<slug>/ds_<slug>_NN.png|.txt
caption 风格对齐 l6liu/he6tou：`<trigger>, <简外观>, <pose/scene>`（短句，逗号分隔）。
"""
import os
import shutil
from typing import Annotated

import typer

from zlog import logger, setup_logging

AUD = "/home/zhaoyiming/z-image-train/output/liulaoliu_story/audition"
DST = "/home/zhaoyiming/z-image-train/datasets"

FU_A = "fu6lao, a stocky middle-aged chinese man, round fleshy face, thin mustache strips, dark shirt"
HUI_A = "huiming, a skinny young chinese pretty-boy, fair face, curly black hair, old oversized dark suit"
HOU_A = "houshaolin, a very tall lean 20-year-old chinese young man, skinny lanky build, receding hairline with balding crown, short messy black hair on the sides, hip-hop streetwear, oversized tee, white sneakers"
TY_A = "tongyuhui, a short stocky 19-year-old chinese youth, round simple face, messy short hair dyed murky grey-white, plain ill-fitting dark jacket"

FU_PICKS = [
 ("fu6lao_01.png", f"{FU_A}, portrait close-up, neutral, plain wall"),
 ("fu6lao_02.png", f"{FU_A}, portrait close-up, scowl, dim light"),
 ("fu6lao_03.png", f"{FU_A}, filter-holder cigarette, portrait close-up, warm light"),
 ("fu6lao_05.png", f"{FU_A}, half body, arms crossed, restaurant doorway"),
 ("fu6lao_06.png", f"{FU_A}, half body, sitting at banquet table, commanding, warm light"),
 ("fu6lao_09.png", f"{FU_A}, work clothes, full body, scrap yard"),
 ("fu6lao_12.png", f"{FU_A}, shiny suit, gold chain, cigar, half body, office"),
 ("fu6lao_13.png", f"{FU_A}, side profile close-up, dark background"),
 ("fu6lao_14.png", f"{FU_A}, three-quarter view, portrait, street"),
 ("fu6lao_15.png", f"{FU_A}, night, neon, smoking, half body"),
 ("fu6lao_16.png", f"{FU_A}, full body, restaurant front at dusk"),
 ("fu6lao_17.png", f"{FU_A}, three-quarter profile, smoking, portrait close-up"),
 ("fu6lao_19.png", f"{FU_A}, full body, walking street, hands in pockets"),
]

HUI_PICKS = [
 ("huiming_bare_01.png", f"{HUI_A}, portrait close-up, neutral, plain wall"),
 ("huiming_bare_02.png", f"{HUI_A}, portrait close-up, smug smile, street"),
 ("huiming_bare_03.png", f"{HUI_A}, portrait close-up, slight frown, dim light"),
 ("huiming_bare_04.png", f"{HUI_A}, adjusting collar, portrait close-up, three-quarter view"),
 ("huiming_bare_05.png", f"{HUI_A}, half body, arms crossed, street"),
 ("huiming_bare_08.png", f"{HUI_A}, half body, leaning on wall, hands in pockets"),
 ("huiming_bare_09.png", f"{HUI_A}, full body, walking, oversized jacket, street"),
 ("huiming_bare_10.png", f"{HUI_A}, full body, slouched, alley"),
 ("huiming_bare_13.png", f"{HUI_A}, side profile close-up, dark background"),
 ("huiming_bare_14.png", f"{HUI_A}, three-quarter view, portrait, street"),
 ("huiming_bare_15.png", f"{HUI_A}, half body, night, street lamp"),
 ("huiming_bare_17.png", f"{HUI_A}, slight smile, portrait close-up, plain wall"),
 ("huiming_bare_18.png", f"{HUI_A}, half body, leaning in, hands clasped, dim room"),
 ("huiming_bare_20.png", f"{HUI_A}, half body, sitting sideways on chair, internet cafe"),
]

HOU_PICKS = [
 ("houshaolin_01.png", f"{HOU_A}, portrait close-up, neutral, plain wall"),
 ("houshaolin_02.png", f"{HOU_A}, portrait close-up, excited animated talking, hand raised"),
 ("houshaolin_03.png", f"{HOU_A}, portrait close-up, cheeky smirk, street"),
 ("houshaolin_04.png", f"{HOU_A}, three-quarter view, small-town street"),
 ("houshaolin_05.png", f"{HOU_A}, side profile close-up, balding crown visible, dark background"),
 ("houshaolin_06.png", f"{HOU_A}, half body, hands in pockets, slouched, street"),
 ("houshaolin_07.png", f"{HOU_A}, half body, arms crossed, leaning on wall"),
 ("houshaolin_10.png", f"{HOU_A}, full body, walking street, oversized tee"),
 ("houshaolin_11.png", f"{HOU_A}, sitting on a stool, shabby hotel room, nervous"),
 ("houshaolin_12.png", f"{HOU_A}, sitting on floor with phone, hoodie, warm lamp light"),
 ("houshaolin_13.png", f"{HOU_A}, half body, barging through doorway"),
 ("houshaolin_15.png", f"{HOU_A}, crouching on curb, gesturing excitedly"),
 ("houshaolin_16.png", f"{HOU_A}, portrait, laughing, head tilted back, street"),
]

TY_PICKS = [
 ("tongyuhui_01.png", f"{TY_A}, portrait close-up, neutral, plain wall"),
 ("tongyuhui_02.png", f"{TY_A}, portrait close-up, puzzled head tilt"),
 ("tongyuhui_03.png", f"{TY_A}, portrait close-up, big simple grin"),
 ("tongyuhui_04.png", f"{TY_A}, three-quarter view, small-town street"),
 ("tongyuhui_05.png", f"{TY_A}, side profile close-up, dark background"),
 ("tongyuhui_06.png", f"{TY_A}, half body, hands clasped in front"),
 ("tongyuhui_07.png", f"{TY_A}, half body, scratching his head"),
 ("tongyuhui_08.png", f"{TY_A}, half body, waving hello, dopey grin"),
 ("tongyuhui_09.png", f"{TY_A}, full body, standing street"),
 ("tongyuhui_10.png", f"{TY_A}, full body, walking street"),
 ("tongyuhui_11.png", f"{TY_A}, sitting hunched on a hotel bed"),
 ("tongyuhui_13.png", f"{TY_A}, full body, green bell-bottom trousers, ill-fitting jacket"),
 ("tongyuhui_14.png", f"{TY_A}, half body, night, street lamp"),
 ("tongyuhui_16.png", f"{TY_A}, portrait, laughing, eyes squeezed shut"),
]

app = typer.Typer(add_completion=False, help="定妆候选 → 训练数据集构建")


def build(subdir, tag, picks, force=False):
    d = os.path.join(DST, tag)
    os.makedirs(d, exist_ok=True)
    n, miss = 0, []
    for i, (src, cap) in enumerate(picks, 1):
        s = os.path.join(AUD, subdir, src)
        if not os.path.exists(s):
            miss.append(src); continue
        base = f"ds_{tag}_{i:02d}"
        png, txt = os.path.join(d, base + ".png"), os.path.join(d, base + ".txt")
        if os.path.exists(png) and not force:
            n += 1; continue
        shutil.copyfile(s, png)
        with open(txt, "w", encoding="utf-8") as f:
            f.write(cap + "\n")
        n += 1
    logger.info(f"[{tag}] {n}/{len(picks)} 张就绪")
    if miss:
        logger.warning(f"[{tag}] ⚠️ 缺失源图: {miss}")
    return len(miss)


@app.command()
def main(
    force: Annotated[bool, typer.Option("--force", help="已存在文件也重新覆盖")] = False,
):
    """把定妆候选按选择清单拷成训练数据集（ds_<slug>_NN.png/.txt）。"""
    setup_logging()
    m1 = build("fu6lao", "fu6lao", FU_PICKS, force)
    m2 = build("huiming_bare", "huiming", HUI_PICKS, force)
    m3 = build("houshaolin", "houshaolin", HOU_PICKS, force)
    m4 = build("tongyuhui", "tongyuhui", TY_PICKS, force)
    logger.success("BUILD DONE" + (f" (缺失 {m1+m2+m3+m4})" if m1 + m2 + m3 + m4 else ""))


if __name__ == "__main__":
    app()

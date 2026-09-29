#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""首批定妆候选：富老大 16(+2补拍) 张 + 刘慧铭 A（戴眼镜）16(+4) 张 + 刘慧铭 B（无眼镜）16(+4) 张。
用法（CLI 基于 typer）：
      cd ~/z-image-train && unset HTTP_PROXY HTTPS_PROXY ALL_PROXY; export NO_PROXY=127.0.0.1,localhost
      python3 -u scripts/gen_audition.py [集合名 ...]   # 可选：fu6lao / huiming / huiming_bare；缺省=全部
输出：~/z-image-train/output/liulaoliu_story/audition/<集合>/  + _manifest.json（幂等：已有文件自动跳过）
说明：候选图用于「用户确认定妆 → 转正为训练数据集」；caption 在数据集阶段再生成。
用户拍板（2026-09-29）：慧铭默认**无眼镜**（B 套定版；强调"高度近视"场景才用 A 套眼镜版）；富老大直接通过。
17~20 号 = 补拍（替补质检偏弱：fu 04/08/11、huiming 06/07/11/12/16）。
原文依据：富老大=四十多岁/1.7m/两撇小胡子/一脸横肉/套过滤嘴香烟；慧铭=白净小脸/自然卷毛/旧西装/俊俏小白脸/高度近视。
日志: loguru → stderr（SKIP/OK/错误/进度）。
"""
import json, time, shutil, urllib.request, os
from typing import Annotated, Optional

import typer

from zlog import logger, setup_logging

BRIDGE = "http://127.0.0.1:8199"
OUT_DIR = "/mnt/d/minimax-h3-demo/ComfyUI/output"
BASE = "/home/zhaoyiming/z-image-train/output/liulaoliu_story/audition"
WF_PATH = "/home/zhaoyiming/.hermes/cache/scratch/z_image_api.json"

app = typer.Typer(add_completion=False, help="定妆候选批量生成（幂等）")

FU = ("a stocky Chinese man in his forties, about 1.7m tall, heavy fleshy brutal face with jowls, "
      "two thin pencil mustache strips, dark short-sleeved shirt, smoking a cigarette held in a filter holder")

HUI_B = ("a skinny young Chinese man, fair delicate pretty-boy face, natural curly black hair, "
         "wearing an old oversized dark suit, shabby faded style")
HUI_G = ("a skinny young Chinese man, fair delicate pretty-boy face, natural curly black hair, "
         "thick-lensed glasses, wearing an old oversized dark suit, shabby faded style")

STYLE = "photorealistic photo, film grain, 35mm"

FU6LAO = [
 ("01", 201, f"Portrait close-up of {FU}, looking at camera, neutral expression, plain wall, soft window light, {STYLE}"),
 ("02", 202, f"Portrait close-up of {FU}, slight scowl, dim indoor light, {STYLE}"),
 ("03", 203, f"Portrait close-up of {FU}, smoking, cigarette in filter holder, warm tungsten light, {STYLE}"),
 ("04", 204, f"Portrait close-up of {FU}, greasy smug grin, restaurant blurred behind, {STYLE}"),
 ("05", 205, f"Half-body of {FU}, standing with arms crossed at a restaurant doorway, afternoon light, {STYLE}"),
 ("06", 206, f"Half-body of {FU}, sitting at a round banquet table full of dishes, one hand raised commanding, warm tungsten, cigarette haze, {STYLE}"),
 ("07", 207, f"Half-body of {FU}, counting a thick stack of cash at a desk, office, lamp light, {STYLE}"),
 ("08", 208, f"Half-body of {FU}, leaning on a black sedan holding a phone, small-town street, {STYLE}"),
 ("09", 209, f"Full-body of {FU}, standing at a scrap collection yard, worn work clothes, daylight, {STYLE}"),
 ("10", 210, f"Full-body of {FU}, walking on a small-town street in a dark suit jacket, {STYLE}"),
 ("11", 211, f"Photo of {FU}, sitting on a sofa in an office, legs crossed, smoking, {STYLE}"),
 ("12", 212, f"Half-body of {FU}, in a shiny suit with a gold chain, cigar, rich boss look, office, {STYLE}"),
 ("13", 213, f"Side profile close-up of {FU}, mustache silhouette, dark background, rim light, {STYLE}"),
 ("14", 214, f"Portrait of {FU}, three-quarter view, street blurred behind, {STYLE}"),
 ("15", 215, f"Half-body of {FU} at night, neon signs, smoking, car lights behind, {STYLE}"),
 ("16", 216, f"Full-body of {FU}, standing in front of his restaurant at dusk, hands in pockets, {STYLE}"),
 ("17", 217, f"Portrait close-up of {FU}, three-quarter profile, smoking, mustache prominent, warm indoor light, {STYLE}"),
 ("18", 218, f"Half-body of {FU}, standing with clasped hands greeting guests at his restaurant door, daytime, {STYLE}"),
 ("19", 220, f"Full-body of {FU}, walking on a small-town street, hands in pockets, dark suit jacket, daylight, {STYLE}"),
]

def huiming_set(H):
    return [
     ("01", 301, f"Portrait close-up of {H}, looking at camera, neutral expression, plain wall, soft window light, {STYLE}"),
     ("02", 302, f"Portrait close-up of {H}, faint smug smile, street blurred behind, {STYLE}"),
     ("03", 303, f"Portrait close-up of {H}, slightly frowning, dim light, {STYLE}"),
     ("04", 304, f"Portrait close-up of {H}, three-quarter view, adjusting his collar, {STYLE}"),
     ("05", 305, f"Half-body of {H}, standing with arms crossed on a small-town street, {STYLE}"),
     ("06", 306, f"Half-body of {H}, bent over a computer desk in a smoky internet cafe, monitor glow, {STYLE}"),
     ("07", 307, f"Half-body of {H}, standing on a swivel chair shouting, internet cafe, {STYLE}"),
     ("08", 308, f"Half-body of {H}, leaning against an arcade wall, hands in pockets, {STYLE}"),
     ("09", 309, f"Full-body of {H}, walking with an oversized suit jacket, small-town street, {STYLE}"),
     ("10", 310, f"Full-body of {H}, standing slouched in a shabby alley, {STYLE}"),
     ("11", 311, f"Photo of {H}, sitting on a swivel chair at an internet cafe, leaning back, {STYLE}"),
     ("12", 312, f"Photo of {H}, sitting on a stool reading a book, warm lamp light, {STYLE}"),
     ("13", 313, f"Side profile close-up of {H}, dark background, rim light, {STYLE}"),
     ("14", 314, f"Portrait of {H}, three-quarter view, street blurred behind, {STYLE}"),
     ("15", 315, f"Half-body of {H} at night under a street lamp, {STYLE}"),
     ("16", 316, f"Half-body of {H} at night, internet cafe monitor glow on his face, {STYLE}"),
     ("17", 317, f"Portrait close-up of {H}, slight confident smile, plain wall, soft light, {STYLE}"),
     ("18", 318, f"Half-body of {H}, leaning in conspiratorially with hands clasped, dim room, {STYLE}"),
     ("19", 319, f"Full-body of {H}, walking at night on a small street, hands in pockets, {STYLE}"),
     ("20", 320, f"Half-body of {H}, sitting sideways on a swivel chair, arm on the backrest, internet cafe, {STYLE}"),
    ]

SETS = {
  "fu6lao": FU6LAO,
  "huiming": huiming_set(HUI_G),
  "huiming_bare": huiming_set(HUI_B),
}

def req(url, data=None):
    r = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None,
                               headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())

def run_set(tag, specs):
    d = os.path.join(BASE, tag)
    os.makedirs(d, exist_ok=True)
    manifest = []
    ok = 0
    for name, seed, prompt in specs:
        dst = os.path.join(d, f"{tag}_{name}.png")
        if os.path.exists(dst) and os.path.getsize(dst) > 10000:
            logger.info(f"[{tag}/{name}] SKIP (exists)"); ok += 1; continue
        wf = json.load(open(WF_PATH))
        wf["27"]["inputs"]["text"] = prompt
        wf["3"]["inputs"]["seed"] = seed
        try:
            resp = req(f"{BRIDGE}/prompt", {"prompt": wf, "client_id": f"audition-{tag}"})
            pid = resp.get("prompt_id")
            if not pid:
                logger.error(f"[{tag}/{name}] SUBMIT FAIL {json.dumps(resp)[:200]}")
                continue
            t0 = time.time()
            while time.time() - t0 < 240:
                time.sleep(2)
                h = req(f"{BRIDGE}/history/{pid}")
                if pid in h and h[pid].get("outputs"):
                    f0 = h[pid]["outputs"]["9"]["images"][0]
                    src = os.path.join(OUT_DIR, f0.get("subfolder", ""), f0["filename"])
                    shutil.copyfile(src, dst)
                    manifest.append({"file": f"{tag}_{name}.png", "seed": seed, "prompt": prompt})
                    logger.info(f"[{tag}/{name}] OK {time.time()-t0:.0f}s")
                    ok += 1
                    break
            else:
                logger.error(f"[{tag}/{name}] TIMEOUT")
        except Exception as e:
            logger.error(f"[{tag}/{name}] ERROR {e}")
    mf = os.path.join(d, "_manifest.json")
    prev = json.load(open(mf)) if os.path.exists(mf) else []
    keep = {m["file"] for m in prev}
    if not manifest:
        manifest = prev
    else:
        manifest = prev + [m for m in manifest if m["file"] not in keep]
    with open(mf, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    logger.success(f"[{tag}] DONE {ok}/{len(specs)}")


@app.command()
def main(
    sets: Annotated[Optional[list[str]], typer.Argument(help="集合名（fu6lao / huiming / huiming_bare），缺省=全部")] = None,
):
    """批量生成定妆候选（幂等：已有文件自动跳过）。"""
    setup_logging()
    wanted = sets or list(SETS)
    for tag in wanted:
        if tag not in SETS:
            logger.warning(f"未知集合: {tag}")
            continue
        run_set(tag, SETS[tag])
    logger.success("AUDITION DONE")


if __name__ == "__main__":
    app()

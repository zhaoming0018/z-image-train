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

# ==== 第二批定妆（2026-09-29 夜）：侯少麟（瘦头陀·左青龙）+ 佟御辉（胖头陀·右白虎）====
# 原文依据（第 5/11/12/13 章）：侯=20岁/1.93m/瘦削/谢顶/嘻哈青年「吆吆吆」；佟=19岁/敦实小个子/胖墩墩/磕巴憨傻/力气大。
# 设定：佟发色取「灰白灰白」稳定态（七巧板多色为第 11 章一次过场，不入训练）；侯保留谢顶（低发际线+头顶稀疏）。
HS = ("a very tall lean 20-year-old Chinese young man, 1.93 meters tall, skinny lanky build, "
      "early balding with a receding hairline and thinning crown, messy short black hair on the sides, "
      "youthful cheeky face, hip-hop street fashion, oversized tee and loose pants, white sneakers")

HOU = [
 ("01", 401, f"Portrait close-up of {HS}, looking at camera, neutral expression, plain wall, soft window light, {STYLE}"),
 ("02", 402, f"Portrait close-up of {HS}, animated excited grin talking with one hand raised, {STYLE}"),
 ("03", 403, f"Portrait close-up of {HS}, cheeky smirk, street blurred behind, {STYLE}"),
 ("04", 404, f"Portrait of {HS}, three-quarter view, small-town street behind, {STYLE}"),
 ("05", 405, f"Side profile close-up of {HS}, balding crown visible, dark background, rim light, {STYLE}"),
 ("06", 406, f"Half-body of {HS}, hands in pockets, slouched on a small-town street, {STYLE}"),
 ("07", 407, f"Half-body of {HS}, arms crossed, leaning against a wall, {STYLE}"),
 ("08", 408, f"Half-body of {HS}, holding a basketball under one arm, street basketball court behind, {STYLE}"),
 ("09", 409, f"Full-body of {HS}, standing on a small-town street, very tall and lanky silhouette, {STYLE}"),
 ("10", 410, f"Full-body of {HS}, walking on a small-town street, oversized tee, hands in pockets, {STYLE}"),
 ("11", 411, f"Photo of {HS}, sitting on a stool in a shabby hotel room, elbows on knees, nervous fidget, {STYLE}"),
 ("12", 412, f"Photo of {HS}, sitting on the floor playing with a phone, hoodie, warm lamp light, {STYLE}"),
 ("13", 413, f"Half-body of {HS}, barging in through a room doorway mid-step, energetic, {STYLE}"),
 ("14", 414, f"Half-body of {HS} at night under a street lamp, hands in pockets, {STYLE}"),
 ("15", 415, f"Photo of {HS}, crouching on a curb gesturing excitedly, {STYLE}"),
 ("16", 416, f"Portrait of {HS}, laughing with head tilted back, street blurred behind, {STYLE}"),
]

TY = ("a short stocky 19-year-old Chinese youth, round simple good-natured face, messy short hair dyed "
      "murky grey-white, plain ill-fitting dark jacket and trousers, sneakers")

TYH = [
 ("01", 501, f"Portrait close-up of {TY}, looking at camera, blank dopey expression, plain wall, soft window light, {STYLE}"),
 ("02", 502, f"Portrait close-up of {TY}, confused head tilt, frowning slightly, {STYLE}"),
 ("03", 503, f"Portrait close-up of {TY}, big open-mouth simple grin, {STYLE}"),
 ("04", 504, f"Portrait of {TY}, three-quarter view, small-town street behind, {STYLE}"),
 ("05", 505, f"Side profile close-up of {TY}, dark background, rim light, {STYLE}"),
 ("06", 506, f"Half-body of {TY}, hands clasped in front, obedient stance, {STYLE}"),
 ("07", 507, f"Half-body of {TY}, scratching his head in confusion, {STYLE}"),
 ("08", 508, f"Half-body of {TY}, waving hello enthusiastically, dopey grin, {STYLE}"),
 ("09", 509, f"Full-body of {TY}, standing on a small-town street, short stocky silhouette, {STYLE}"),
 ("10", 510, f"Full-body of {TY}, walking on a small-town street, slightly clumsy stride, {STYLE}"),
 ("11", 511, f"Photo of {TY}, sitting hunched on a bed in a shabby hotel room, {STYLE}"),
 ("12", 512, f"Photo of {TY}, squatting on a curb eating a steamed bun, {STYLE}"),
 ("13", 513, f"Full-body of {TY}, green bell-bottom trousers and long-sleeve jacket, comical ill-fitting outfit, {STYLE}"),
 ("14", 514, f"Half-body of {TY} at night under a street lamp, {STYLE}"),
 ("15", 515, f"Photo of {TY}, peeking out from behind a room doorway, nervous, {STYLE}"),
 ("16", 516, f"Portrait of {TY}, laughing dumbly with eyes squeezed shut, {STYLE}"),
]

SETS = {
  "fu6lao": FU6LAO,
  "huiming": huiming_set(HUI_G),
  "huiming_bare": huiming_set(HUI_B),
  "houshaolin": HOU,
  "tongyuhui": TYH,
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

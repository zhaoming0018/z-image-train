#!/usr/bin/env python3
"""动漫人物卡批次：12 角色 × 四视角参考卡（Qwen-Image 2.1，1536×1024）。
产出：output/liulaoliu_story/sheets/card_<slug>_anime.png（老六已有卡，不在批内）。
"""
import json
import os
import shutil
import time
import urllib.request
from pathlib import Path

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)

ROOT = "/home/zhaoyiming/z-image-train"
BRIDGE = "http://127.0.0.1:8199"
COMFY_OUT = "/mnt/d/minimax-h3-demo/ComfyUI/output"
DEST = Path(f"{ROOT}/output/liulaoliu_story/sheets")
DEST.mkdir(parents=True, exist_ok=True)

TEMPLATE = ("anime character reference sheet, 2D anime style, clean cel-shaded illustration: {feat}; "
            "character design sheet with 4 views arranged in a horizontal row from left to right: "
            "large close-up head portrait, front standing full body view, side view full body, back view full body; "
            "the same character in all views, consistent outfit and proportions, plain white background, "
            "anime cel shading, flat colors, clean line art, no text")

CHARS = [
    ("he6tou", "an elderly dark-skinned Chinese fortune-teller, grey-white messy hair, deep wrinkles, "
               "wearing a shabby grey-brown old jacket"),
    ("fu6lao", "a stocky Chinese man in his forties, heavy fleshy brutal face with jowls, two thin pencil "
               "mustache strips, dark short-sleeved shirt, holding a cigarette in a filter holder"),
    ("huiming", "a skinny young Chinese pretty-boy, fair face, natural curly black hair, wearing an old "
                "oversized dark suit, shabby faded style"),
    ("houshaolin", "a very tall lean Chinese young man, skinny lanky build, early balding with a receding "
                   "hairline and messy short black hair on the sides, youthful cheeky face, hip-hop street "
                   "fashion, oversized tee and loose pants, white sneakers"),
    ("tongyuhui", "a short stocky Chinese youth, round good-natured face, messy short hair dyed murky "
                  "grey-white, wearing a plain ill-fitting dark jacket and trousers, sneakers"),
    ("caoda", "a very tall heavily-built young Chinese man in his early twenties, hulking broad frame like "
              "a wall, fleshy rounded face with small narrow eyes, short black hair, plain dark jacket over "
              "a t-shirt, holding a large plastic cola bottle"),
    ("zhanglei", "a slim energetic Chinese young man in his mid-twenties, natural curly black hair with a "
                 "distinctive single curly forelock hanging over his forehead, plain casual work clothes, "
                 "a small dark messenger bag slung across his shoulder"),
    ("lixiaowei", "a slim young Chinese civil servant in his early twenties, fair delicate boyish face, short "
                  "neat black hair, earnest expression, wearing a dark navy civil-service uniform jacket with "
                  "a matching peaked cap"),
    ("luming", "a lean young Chinese man in his early twenties, short buzz-cut black hair, narrow eyes, thin "
               "sharp face, wearing a dark navy Chinese police uniform jacket with shoulder epaulettes and a "
               "matching peaked cap"),
    ("mengxiaoyan", "a slim young Chinese woman in her early twenties, fair skin, ordinary girl-next-door "
                    "face, both mouth corners distinctively upturned in little hook-like curves, shoulder-length "
                    "black hair, wearing a crisp white shirt"),
    ("yantouer", "a burly Chinese man in his early thirties, short black hair, simple honest face, plain "
                 "dark work clothes"),
    ("mawangye", "a tall powerfully built Chinese man in his mid-thirties, muscular broad-shouldered frame "
                 "like an underground boxing boss, short black hair slicked back, thick dark eyebrows, narrow "
                 "piercing eyes, a hard menacing face, wearing a black jacket over a dark shirt"),
]
SEED = 7


def submit(wf):
    body = json.dumps({"prompt": wf}).encode()
    req = urllib.request.Request(BRIDGE + "/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))["prompt_id"]


def wait_done(pid, timeout=900):
    t0 = time.time()
    while time.time() - t0 < timeout:
        with urllib.request.urlopen(f"{BRIDGE}/history/{pid}", timeout=30) as r:
            h = json.load(r)
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "error":
                return h[pid]
        time.sleep(3)
    raise TimeoutError(pid)


tpl = json.load(open(f"{ROOT}/config/qwen21_api.json"))
done, skipped = [], []
for slug, feat in CHARS:
    out = DEST / f"card_{slug}_anime.png"
    if out.exists():
        skipped.append(slug)
        print(f"[skip] {slug} (exists)", flush=True)
        continue
    wf = json.loads(json.dumps(tpl))
    wf["4"]["inputs"]["prompt"] = TEMPLATE.format(feat=feat)
    wf["6"]["inputs"]["seed"] = SEED
    wf["5"]["inputs"]["width"] = 1536
    wf["5"]["inputs"]["height"] = 1024
    wf["9"]["inputs"]["filename_prefix"] = f"card_{slug}_anime"
    t0 = time.time()
    pid = submit(wf)
    res = wait_done(pid)
    got = False
    for node_out in res.get("outputs", {}).values():
        for img in node_out.get("images", []):
            src = os.path.join(COMFY_OUT, img.get("subfolder", ""), img["filename"])
            if src.lower().endswith((".png", ".jpg", ".webp")):
                shutil.copy(src, out)
                print(f"[card] {slug} {time.time()-t0:.1f}s -> {out}", flush=True)
                got = True
    if not got:
        print(f"[FAIL] {slug}", flush=True)
    else:
        done.append(slug)

print(f"ALL_DONE done={len(done)} skipped={len(skipped)}", flush=True)

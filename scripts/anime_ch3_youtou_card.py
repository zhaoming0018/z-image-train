#!/usr/bin/env python3
"""第三章新角色『油头』角色卡（四视角 sheet，纯文描，qwen21_api.json）。"""
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

TEMPLATE = ("anime character reference sheet, 2D anime style, clean cel-shaded illustration: {feat}; "
            "character design sheet with 4 views arranged in a horizontal row from left to right: "
            "large close-up head portrait, front standing full body view, side view full body, back view full body; "
            "the same character in all views, consistent outfit and proportions, plain white background, "
            "anime cel shading, flat colors, clean line art, no text")
FEAT = ("a fat middle-aged Chinese restaurant owner, completely bald with a shiny oily head, thick neck, an "
        "enormous belly bulging far over his waistband, wearing a ragged white undershirt and loose dark pants, "
        "fierce face with bushy eyebrows, small mean eyes and thick stubble")


def submit(wf):
    req = urllib.request.Request(BRIDGE + "/prompt", data=json.dumps({"prompt": wf}).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))["prompt_id"]


tpl = json.load(open(f"{ROOT}/config/qwen21_api.json"))
wf = json.loads(json.dumps(tpl))
wf["4"]["inputs"]["prompt"] = TEMPLATE.format(feat=FEAT)
wf["6"]["inputs"]["seed"] = 8
wf["5"]["inputs"]["width"] = 1536
wf["5"]["inputs"]["height"] = 1024
wf["9"]["inputs"]["filename_prefix"] = "card_youtou_anime"

t0 = time.time()
pid = submit(wf)
while time.time() - t0 < 3600:
    with urllib.request.urlopen(f"{BRIDGE}/history/{pid}", timeout=30) as r:
        h = json.load(r)
    if pid in h:
        break
    time.sleep(3)
out = DEST / "card_youtou_anime.png"
for node_out in h[pid].get("outputs", {}).values():
    for img in node_out.get("images", []):
        src = os.path.join(COMFY_OUT, img.get("subfolder", ""), img["filename"])
        if src.lower().endswith((".png", ".jpg", ".webp")):
            shutil.copy(src, out)
            print(f"[card] {time.time()-t0:.1f}s -> {out}", flush=True)
print("DONE", flush=True)

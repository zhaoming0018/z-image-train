#!/usr/bin/env python3
"""第一章第一镜（s1_strut）动漫风重制：用老六动漫卡做参考图锁人。"""
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

PROMPT = ("anime style illustration, 2D cel shaded, clean line art: the chubby young man from the reference image, "
          "a 23-year-old Chinese street punk with a round face and small squinting triangular eyes, wearing a plain white "
          "ribbed tank top, dark knee-length shorts and black flip-flops, small pot belly; he is strutting toward the camera, "
          "hands in pockets, cocky lazy grin, shoulders slightly swaying; background: an old Chinese neighborhood street "
          "with roller shutter doors, yellow shop signs with red Chinese characters, red vertical sign, plastic stools and "
          "buckets on the roadside, blurred pedestrians; center composition, near full body, eye-level slightly low angle, "
          "soft diffused daylight, warm grey low-saturation palette with red and yellow accents, anime key visual, no watermark")
SEED = 47


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


wf = json.load(open(f"{ROOT}/config/qwen21_ref_api.json"))
wf["10"]["inputs"]["image"] = "l6_anime_card.png"
wf["4"]["inputs"]["prompt"] = PROMPT
wf["6"]["inputs"]["seed"] = SEED
wf["5"]["inputs"]["width"] = 1536
wf["5"]["inputs"]["height"] = 1024
wf["9"]["inputs"]["filename_prefix"] = "anime_ch1_s1_strut"
t0 = time.time()
pid = submit(wf)
res = wait_done(pid)
for node_out in res.get("outputs", {}).values():
    for img in node_out.get("images", []):
        src = os.path.join(COMFY_OUT, img.get("subfolder", ""), img["filename"])
        if src.lower().endswith((".png", ".jpg", ".webp")):
            dst = DEST / "anime_ch1_s1_strut.png"
            shutil.copy(src, dst)
            shutil.copy(src, "/mnt/d/第一章样片_动漫风_s1.png")
            print(f"{time.time()-t0:.1f}s -> {dst}", flush=True)
print("ALL_DONE", flush=True)

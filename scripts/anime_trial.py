#!/usr/bin/env python3
"""动漫风转向试验：老六「四视角人物卡」双模型 A/B（AnythingXL vs Qwen-Image 2.1）。
产出：/mnt/d/动漫试验_A_AnythingXL.png、/mnt/d/动漫试验_B_Qwen.png
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

PROMPT = ("anime character reference sheet, 2D anime style, clean cel-shaded illustration: "
          "a chubby 23-year-old Chinese young man with a round face, short messy black hair, "
          "small squinting triangular eyes, puffy cheeks, wearing a plain white ribbed tank top, "
          "dark knee-length shorts and black flip-flops, small pot belly; "
          "character design sheet with 4 views arranged in a horizontal row from left to right: "
          "large close-up head portrait, front standing full body view, side view full body, back view full body; "
          "the same character in all views, consistent outfit and proportions, plain white background, "
          "anime cel shading, flat colors, clean line art, no text")


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


def collect(res, dst):
    for node_out in res.get("outputs", {}).values():
        for img in node_out.get("images", []):
            src = os.path.join(COMFY_OUT, img.get("subfolder", ""), img["filename"])
            if os.path.exists(src) and src.lower().endswith((".png", ".jpg", ".webp")):
                shutil.copy(src, dst)
                return dst
    raise RuntimeError("no image output")


# --- A: AnythingXL (SDXL) ---
wf = json.load(open(f"{ROOT}/config/anime_sdxl_api.json"))
wf["2"]["inputs"]["text"] = PROMPT
wf["5"]["inputs"]["seed"] = 42
wf["7"]["inputs"]["filename_prefix"] = "anime_trial_sdxl"
t0 = time.time()
pid = submit(wf)
res = wait_done(pid)
outA = collect(res, DEST / "anime_trial_A_anythingxl.png")
shutil.copy(outA, "/mnt/d/动漫试验_A_AnythingXL.png")
print(f"[A] AnythingXL {time.time()-t0:.1f}s -> {outA}", flush=True)

# --- B: Qwen-Image 2.1 ---
wf = json.load(open(f"{ROOT}/config/qwen21_api.json"))
wf["4"]["inputs"]["prompt"] = PROMPT
wf["6"]["inputs"]["seed"] = 42
wf["5"]["inputs"]["width"] = 1536
wf["5"]["inputs"]["height"] = 1024
wf["9"]["inputs"]["filename_prefix"] = "anime_trial_qwen"
t0 = time.time()
pid = submit(wf)
res = wait_done(pid)
outB = collect(res, DEST / "anime_trial_B_qwen.png")
shutil.copy(outB, "/mnt/d/动漫试验_B_Qwen.png")
print(f"[B] Qwen {time.time()-t0:.1f}s -> {outB}", flush=True)
print("ALL_DONE", flush=True)

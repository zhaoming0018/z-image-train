#!/usr/bin/env python3
"""第三章试片：油头举刀砍老六 —— 首帧图（低角度仰拍构图，为5秒动作镜准备）。"""
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
INPUT = "/mnt/d/minimax-h3-demo/ComfyUI/input"

STYLE = ("Japanese anime style illustration, a still frame from a TV anime, cel shading, clean line art, "
         "simple flat anime background: ")
NEG = ("photorealistic, photo, 3d render, gradient shading, grunge, painterly, detailed background, "
       "extra people, duplicate person")

NAME = "anime_ch3test_fist"
SEED = 165

body = ("in a wrecked old Chinese restaurant private room, low camera angle looking slightly up at the two men: the "
        "bald fat boss from the SECOND reference image — shiny bald head, huge belly, white undershirt, furious face "
        "— crouches low on the floor, swinging a big Chinese watermelon knife upward toward the chubby young man "
        "with short black hair from the FIRST reference image, who stands to the side in a low crouch with one fist "
        "clenched; overturned chairs and a toppled round table, broken glass and scattered beer bottles on the floor; "
        "the two men look clearly different — the young man has a round face and hair, the boss is bald with stubble "
        "and much older; exactly two people in the whole scene, no duplicates")
prompt = STYLE + body + "; everything simple, clean and flat, clearly a hand-drawn anime scene, warm pastel cel colors"

shutil.copy(f"{DEST}/card_l6liu_anime.png", f"{INPUT}/card_l6liu_anime.png")
shutil.copy(f"{DEST}/card_youtou_anime.png", f"{INPUT}/card_youtou_anime.png")

tpl = json.load(open(f"{ROOT}/config/qwen21_ref_api.json"))
wf = json.loads(json.dumps(tpl))
wf["10"]["inputs"]["image"] = "card_l6liu_anime.png"
wf["11"] = {"class_type": "LoadImage", "inputs": {"image": "card_youtou_anime.png"}}
wf["4"]["inputs"]["images.image_2"] = ["11", 0]
wf["4"]["inputs"]["prompt"] = prompt
wf["4"]["inputs"]["negative_prompt"] = NEG
wf["6"]["inputs"]["seed"] = SEED
wf["5"]["inputs"]["width"] = 1536
wf["5"]["inputs"]["height"] = 1024
wf["9"]["inputs"]["filename_prefix"] = NAME


def submit(wf):
    req = urllib.request.Request(BRIDGE + "/prompt", data=json.dumps({"prompt": wf}).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))["prompt_id"]


t0 = time.time()
pid = submit(wf)
while time.time() - t0 < 3600:
    with urllib.request.urlopen(f"{BRIDGE}/history/{pid}", timeout=30) as r:
        h = json.load(r)
    if pid in h:
        break
    time.sleep(3)
out = DEST / f"{NAME}.png"
for node_out in h[pid].get("outputs", {}).values():
    for img in node_out.get("images", []):
        src = os.path.join(COMFY_OUT, img.get("subfolder", ""), img["filename"])
        if src.lower().endswith((".png", ".jpg", ".webp")):
            shutil.copy(src, out)
            print(f"[still] {time.time()-t0:.1f}s -> {out}", flush=True)
print("DONE", flush=True)

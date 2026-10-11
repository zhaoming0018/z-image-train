#!/usr/bin/env python3
"""第一章 s2-s5 动漫重制（双参考锁人：image_1=黑老头卡, image_2=老六卡）。"""
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

STYLE = ("Japanese anime style illustration, a still frame from a TV anime, cel shading, clean line art, "
         "simple flat anime background: ")
TAIL = ("; background: an old Chinese neighborhood street drawn as a simple anime background — simplified "
        "building shapes, flat pastel-colored walls, minimal detail, soft flat cel shadows; everything simple, "
        "clean and flat, clearly a hand-drawn anime scene, not realistic, no photo texture; "
        "center composition, warm pastel anime color design")
NEG = ("photorealistic, realistic texture, photo, 3d render, gradient shading, complex lighting, grunge, dirt, "
       "painterly, detailed background, extra people")

L6 = "the chubby young man from the second reference image (white ribbed tank top, dark knee-length shorts, black flip-flops, round face, small squinting eyes)"
HE = "the elderly dark-skinned fortune-teller from the first reference image (grey-white messy hair, deep wrinkles, shabby grey-brown old jacket)"

SHOTS = [
    ("s2_block", 71,
     f"two men on a street: {HE} standing blocking the way with one black hand raised palm-out, "
     f"and {L6} leaning forward with startled wide eyes, hands at his sides"),
    ("s3_shake", 72,
     f"two men sitting face to face on low stools beside a simple fortune-telling mat on the ground: "
     f"{L6} is shaking a bamboo fortune-stick tube with both hands, grinning; {HE} sits opposite leaning "
     f"forward watching him"),
    ("s4_palm", 73,
     f"medium shot: {L6} crouching, raising one palm out toward the other, frowning and arguing; "
     f"{HE} beside him gesturing with both hands as if explaining, calm"),
    ("s5_stool", 74,
     f"the chubby young man {L6} lunging forward raising a small wooden stool high overhead about to slam it down, "
     f"furious; {HE} crouching on the ground below shrinking away with both hands covering his face"),
]


def submit(wf):
    body = json.dumps({"prompt": wf}).encode()
    req = urllib.request.Request(BRIDGE + "/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))["prompt_id"]


def wait_done(pid, timeout=1200):
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


tpl = json.load(open(f"{ROOT}/config/qwen21_ref_api.json"))
for name, seed, body in SHOTS:
    wf = json.loads(json.dumps(tpl))
    wf["10"]["inputs"]["image"] = "card_he6tou_anime.png"          # image_1 = 黑老头
    wf["11"] = {"class_type": "LoadImage", "inputs": {"image": "card_l6liu_anime.png"}}  # image_2 = 老六
    wf["4"]["inputs"]["images.image_2"] = ["11", 0]
    wf["4"]["inputs"]["prompt"] = STYLE + body + TAIL
    wf["4"]["inputs"]["negative_prompt"] = NEG
    wf["6"]["inputs"]["seed"] = seed
    wf["5"]["inputs"]["width"] = 1536
    wf["5"]["inputs"]["height"] = 1024
    wf["9"]["inputs"]["filename_prefix"] = f"anime_ch1_{name}"
    t0 = time.time()
    pid = submit(wf)
    res = wait_done(pid)
    for node_out in res.get("outputs", {}).values():
        for img in node_out.get("images", []):
            src = os.path.join(COMFY_OUT, img.get("subfolder", ""), img["filename"])
            if src.lower().endswith((".png", ".jpg", ".webp")):
                shutil.copy(src, DEST / f"anime_ch1_{name}.png")
                print(f"[{name}] seed={seed} {time.time()-t0:.1f}s ok", flush=True)
print("ALL_DONE", flush=True)

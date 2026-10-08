#!/usr/bin/env python3
"""第二章动漫集 · 6 张分镜图（Qwen 参考图锁人；双人镜头双参考）。
产出：output/liulaoliu_story/sheets/anime_ch2_sN_*.png；已存在自动跳过。
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
INPUT = "/mnt/d/minimax-h3-demo/ComfyUI/input"

STYLE = ("Japanese anime style illustration, a still frame from a TV anime, cel shading, clean line art, "
         "simple flat anime background: ")
TAIL = ("; everything simple, clean and flat, clearly a hand-drawn anime scene, not realistic, no photo texture; "
        "warm pastel anime color design")
NEG = ("photorealistic, photo, 3d render, gradient shading, grunge, painterly, detailed background, "
       "extra people, duplicate person")

L6 = "the chubby young man from the {ref} reference image (white ribbed tank top, dark shorts, flip-flops)"

SHOTS = [
    # (name, seed, refs[list of card files], prompt)
    ("s1_sign", 87, ["card_l6liu_anime.png"],
     "the chubby young man from the reference image (white ribbed tank top, dark shorts, flip-flops) stands ALONE "
     "at the entrance of an old hotpot restaurant, head tilted looking up at its big worn signboard with the Chinese "
     "characters 「北台肥羊」; the street is an old Chinese lane with cluttered small shopfronts but completely "
     "empty of other people — only one young man in the whole scene, no pedestrians; near full body, warm evening light"),
    ("s2_frontdesk", 82, ["card_l6liu_anime.png"],
     "the chubby young man from the reference image pushes through the entrance door of an old hotpot restaurant "
     "into a steamy main hall; a plump cheerful young Chinese waitress with a ponytail in a cheap pink uniform "
     "greets him from the front counter; steam and warm haze, simple flat anime interior"),
    ("s3_manager", 88, ["card_l6liu_anime.png"],
     "the chubby young man from the reference image stands in the cluttered first-floor hall of an old hotpot "
     "restaurant — exactly ONE chubby young man in the whole scene; a middle-aged fawning restaurant manager in a "
     "dark vest leans in pointing up with a sly smile; other diners are distant simple background blurs clearly "
     "different from the main character; crowded tables and chairs, simple flat anime interior"),
    ("s4_slam", 89, ["card_fu6lao_anime.png", "card_l6liu_anime.png"],
     "inside a private room of an old hotpot restaurant: EXACTLY TWO people in the room — the stocky middle-aged "
     "man with jowls and a pencil mustache from the first reference image sits at the head of the round table, "
     "one hand slamming down on the tabletop furiously; the chubby young man from the second reference image "
     "stands beside him shrinking, shoulders hunched, with a fawning apologetic smile; no other people; "
     "round table with dishes, simple flat anime interior"),
    ("s5_flee", 85, ["card_fu6lao_anime.png", "card_l6liu_anime.png"],
     "inside a private room: the chubby young man from the second reference image hurries out through the door "
     "bowing apologetically; behind him the stocky middle-aged man from the first reference image sits at the "
     "table glaring and yelling; simple flat anime interior"),
    ("s6_netbar", 90, ["card_huiming_anime.png", "card_l6liu_anime.png"],
     "inside a smoky old internet cafe with rows of old CRT monitors: EXACTLY TWO people — the skinny young man in "
     "a shabby oversized worn dark suit from the first reference image stands ON TOP of a chair, mouth wide open "
     "yelling, one arm raised; the chubby young man from the second reference image below kicks that chair with "
     "one raised foot; no other people; rows of computers and dim lighting, simple flat anime interior"),
]

# 先同步所有卡图到 input（防缺图）
needed = set()
for _, _, refs, _ in SHOTS:
    needed.update(refs)
for r in sorted(needed):
    shutil.copy(f"{DEST}/{r}", f"{INPUT}/{r}")
print("[prep] cards synced:", sorted(needed), flush=True)


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


tpl = json.load(open(f"{ROOT}/config/qwen21_ref_api.json"))
for name, seed, refs, body in SHOTS:
    out = DEST / f"anime_ch2_{name}.png"
    if out.exists():
        print(f"[skip] {name} (exists)", flush=True)
        continue
    wf = json.loads(json.dumps(tpl))
    wf["10"]["inputs"]["image"] = refs[0]                      # image_1
    if len(refs) > 1:
        wf["11"] = {"class_type": "LoadImage", "inputs": {"image": refs[1]}}   # image_2
        wf["4"]["inputs"]["images.image_2"] = ["11", 0]
    wf["4"]["inputs"]["prompt"] = STYLE + body + TAIL
    wf["4"]["inputs"]["negative_prompt"] = NEG
    wf["6"]["inputs"]["seed"] = seed
    wf["5"]["inputs"]["width"] = 1536
    wf["5"]["inputs"]["height"] = 1024
    wf["9"]["inputs"]["filename_prefix"] = f"anime_ch2_{name}"
    t0 = time.time()
    pid = submit(wf)
    res = wait_done(pid)
    got = False
    for node_out in res.get("outputs", {}).values():
        for img in node_out.get("images", []):
            src = os.path.join(COMFY_OUT, img.get("subfolder", ""), img["filename"])
            if src.lower().endswith((".png", ".jpg", ".webp")):
                shutil.copy(src, out)
                print(f"[still] {name} {time.time()-t0:.1f}s -> {out.name}", flush=True)
                got = True
    if not got:
        print(f"[FAIL] {name}", flush=True)
print("ALL_DONE", flush=True)

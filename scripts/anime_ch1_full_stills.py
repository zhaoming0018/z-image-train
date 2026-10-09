#!/usr/bin/env python3
"""第一章完整版 · 新增 8 张分镜图（Qwen 参考图锁人；单/双参考自适应）。
产出：output/liulaoliu_story/sheets/anime_ch1full_n*.png；已存在自动跳过。
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

SHOTS = [
    ("n1_crouch", 91, ["card_l6liu_anime.png"],
     "the chubby young man from the reference image (white ribbed tank top, dark shorts, flip-flops) squats on a "
     "street curb beside an old scrap-station wall, smoking a cheap cigarette with a tired cynical expression; "
     "only one young man, no other people; simple flat anime street background"),
    ("n2_excited", 92, ["card_l6liu_anime.png"],
     "the chubby young man from the reference image stands on the street raising both fists to the sky, looking up "
     "with a bright excited grin, dreaming of hitting the big time; only one young man, no other people; "
     "simple flat anime street background"),
    ("n3_booth", 111, ["card_l6liu_anime.png", "card_he6tou_anime.png"],
     "on a small street corner: a shabby fortune-teller booth with no table — a worn cloth spread on the ground "
     "painted with a wrinkly eight-trigram bagua that looks like a flatbread, beside it a crudely painted palm with "
     "claw-like fingers, a bamboo chopstick-holder used as a fortune-stick tube and a tiny wooden stool; the chubby "
     "young man from the first reference image stands looking down at the booth — only ONE young man, do not "
     "duplicate him, exactly two people in total in the scene; the elderly dark-skinned fortune-teller from the "
     "second reference image sits cross-legged beside the booth grinning up at him; no other people; "
     "simple flat anime background"),
    ("n4_probe", 94, ["card_he6tou_anime.png"],
     "close-up: the elderly dark-skinned fortune-teller from the reference image leans forward with a sly filthy "
     "grin, rubbing his dirty hands together, scheming; only one person; simple flat anime background"),
    ("n5_smash", 95, ["card_l6liu_anime.png"],
     "the chubby young man from the reference image suddenly explodes in anger — he flings a bamboo fortune-stick "
     "tube down to the ground, sticks scattering everywhere, mouth wide open shouting furiously; "
     "only one young man, no other people; simple flat anime street background"),
    ("n6_grip", 113, ["card_l6liu_anime.png", "card_he6tou_anime.png"],
     "wide shot, full bodies: on the street, the elderly dark-skinned fortune-teller from the second reference image "
     "suddenly grabs the wrist of the chubby young man from the first reference image like an iron clamp; the young "
     "man pulls back startled, leaning away with a shocked grimace; both figures fully visible, medium-small in the "
     "frame; the grabbing gesture reads through arm positions, simple clean anime shapes, hands simple and small; "
     "no other people; simple flat anime background"),
    ("n7_palm", 97, ["card_l6liu_anime.png", "card_he6tou_anime.png"],
     "close-up: the elderly dark-skinned fortune-teller from the second reference image holds the open palm of the "
     "chubby young man from the first reference image and draws lines on it with one dirty finger, chanting "
     "mysteriously with narrowed eyes; the young man's face shows growing panic; no other people; "
     "simple flat anime background"),
    ("n8_flushed", 98, ["card_l6liu_anime.png"],
     "close-up portrait of the chubby young man from the reference image with a layer of cold sweat on his face, "
     "eyes wide in alarm and disbelief, biting his lip in panic; only one person; simple flat anime background"),
]

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


def wait_done(pid, timeout=3600):
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
    out = DEST / f"anime_ch1full_{name}.png"
    if out.exists():
        print(f"[skip] {name} (exists)", flush=True)
        continue
    wf = json.loads(json.dumps(tpl))
    wf["10"]["inputs"]["image"] = refs[0]
    if len(refs) > 1:
        wf["11"] = {"class_type": "LoadImage", "inputs": {"image": refs[1]}}
        wf["4"]["inputs"]["images.image_2"] = ["11", 0]
    wf["4"]["inputs"]["prompt"] = STYLE + body + TAIL
    wf["4"]["inputs"]["negative_prompt"] = NEG
    wf["6"]["inputs"]["seed"] = seed
    wf["5"]["inputs"]["width"] = 1536
    wf["5"]["inputs"]["height"] = 1024
    wf["9"]["inputs"]["filename_prefix"] = f"anime_ch1full_{name}"
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

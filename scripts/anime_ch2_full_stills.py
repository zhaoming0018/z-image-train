#!/usr/bin/env python3
"""第二章完整版 · 新增 11 张分镜图（Qwen 参考图锁人）。
产出：output/liulaoliu_story/sheets/anime_ch2full_f*.png；已存在自动跳过。
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
    ("f01_street", 141, ["card_l6liu_anime.png"],
     "a busy small-town Chinese commercial lane with cluttered mismatched shopfronts — a noodle shop beside a repair "
     "garage, a KTV beside a yoga studio, an old internet cafe; the chubby young man from the reference image walks "
     "into the frame with a swagger, hands in pockets; only one young man, no other people; wide street view"),
    ("f03_hotpot", 142, ["card_l6liu_anime.png"],
     "the chubby young man from the reference image pushes open the glass door of an old hotpot restaurant, a wave "
     "of steam and heat rushing out at him, his face grimacing and holding his breath; warm hazy interior; "
     "only one young man, no other people"),
    ("f04_dismiss", 143, ["card_l6liu_anime.png"],
     "the chubby young man from the reference image walks down the small street waving one hand dismissively with a "
     "sour cynical face, head turned away like refusing to look at something behind him; only one young man, "
     "no other people; simple flat anime street"),
    ("f07_stairs", 144, ["card_l6liu_anime.png"],
     "the chubby young man from the reference image squeezes up a narrow cramped staircase of an old restaurant, "
     "past stacked folding tables and chairs, twisting his body sideways to get through; only one young man, "
     "no other people; simple flat anime interior"),
    ("f08_boss", 152, ["card_fu6lao_anime.png", "card_l6liu_anime.png"],
     "inside the private room: the stocky middle-aged boss with jowls and a pencil mustache from the first reference "
     "image sits at the head of the round table with a cigarette in his mouth, looking up; the chubby young man from "
     "the second reference image stands at the door greeting him with a small nod and a raised hand; "
     "exactly two people, no duplicates; simple flat anime interior"),
    ("f09_fawn", 153, ["card_fu6lao_anime.png", "card_l6liu_anime.png"],
     "inside the private room: the chubby young man from the second reference image bows slightly with a fawning "
     "apologetic smile, hands clasped together in front of his chest with clear simple anime hands; the stocky "
     "middle-aged boss with the pencil mustache from the first reference image sits behind the round table looking "
     "at him unimpressed; exactly two people, no duplicates; simple flat anime interior"),
    ("f11_light", 147, ["card_fu6lao_anime.png", "card_l6liu_anime.png"],
     "inside the private room: the chubby young man from the second reference image bends over deferentially, gently "
     "guiding the stocky boss's hand — the boss from the first reference image sits holding a cigarette and lets his "
     "hand be guided back to his mouth, half-annoyed half-amused; exactly two people, no duplicates; "
     "simple flat anime interior"),
    ("f12_lean", 148, ["card_fu6lao_anime.png", "card_l6liu_anime.png"],
     "inside the private room: the stocky boss with jowls and pencil mustache from the first reference image leans "
     "back comfortably in his chair, eyes narrowed, smoking and waving one hand dismissively as he gives orders; the "
     "chubby young man from the second reference image stands listening obediently; exactly two people, "
     "no duplicates; simple flat anime interior"),
    ("f14_cigs", 154, ["card_l6liu_anime.png"],
     "the chubby young man from the reference image walks out of the restaurant door onto the street, slipping a "
     "small pack of cigarettes into the waistband of his shorts with a small relieved smirk; only one young man, "
     "no other people; simple flat anime street"),
    ("f15_netbar", 155, ["card_l6liu_anime.png"],
     "interior of a noisy smoky old internet cafe: rows of old CRT monitors with glowing screens, messy desks; the "
     "chubby young man from the reference image squeezes sideways between two rows of chairs — only ONE young man in "
     "the whole scene, do not duplicate him; the background players are anonymous dark blurry silhouettes very far "
     "away, clearly different from him"),
    ("f18_screen", 157, ["card_huiming_anime.png", "card_l6liu_anime.png"],
     "inside the internet cafe: the skinny young man in a shabby oversized suit from the first reference image sits "
     "at the computer desk with a mouse in his hand, looking up annoyed; the chubby young man from the second "
     "reference image pulls at the SKINNY MAN'S sleeve — he pulls the skinny man, not himself; exactly two people "
     "in the whole scene — the skinny man and ONE young man, absolutely no second young man anywhere in the frame, "
     "no duplicates; rows of CRT monitors; simple flat anime interior"),
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
    out = DEST / f"anime_ch2full_{name}.png"
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
    wf["9"]["inputs"]["filename_prefix"] = f"anime_ch2full_{name}"
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

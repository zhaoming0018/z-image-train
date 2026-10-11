#!/usr/bin/env python3
"""第一章动漫集 · 台词版 s2-s5 逐镜 i2v（H3 原生中文台词写进 prompt）。
s1 台词版单独跑（h3_ep1_s1_line）。产出：WORK/ep1_sN_line.mp4；已存在自动跳过。
"""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = "/home/zhaoyiming/z-image-train"
WORK = Path("/home/zhaoyiming/.hermes/cache/scratch/ep1")
WORK.mkdir(parents=True, exist_ok=True)
VIDEO_DIR = Path("/mnt/d/minimax-h3-demo/ComfyUI/output/video")
INPUT_DIR = "/mnt/d/minimax-h3-demo/ComfyUI/input"
SCRATCH = "/home/zhaoyiming/.hermes/cache/scratch"
WF_SRC = "/mnt/d/minimax-h3-demo/workflows/video_minimax_h3_i2v.json"

SHOTS = [
    ("s2_block", 192, "anime_ch1_s2_block.png",
     "anime style 2D animation, cel-shaded: the elderly fortune-teller raises his dark hand to block the way and "
     "says in Chinese: 「小朋友，你今天有挂，六爷是吧？」; the chubby young man jerks back startled with wide eyes; "
     "the flat simple anime background stays unchanged; smooth limited TV-anime animation"),
    ("s3_shake", 193, "anime_ch1_s3_shake.png",
     "anime style 2D animation, cel-shaded: the chubby young man shakes the bamboo fortune-stick tube briskly and "
     "says to the old man in Chinese: 「你是饭馆退休的吧？」; the old fortune-teller leans forward watching him; "
     "the flat simple anime background stays unchanged; smooth limited TV-anime animation"),
    ("s4_palm", 194, "anime_ch1_s4_palm.png",
     "anime style 2D animation, cel-shaded: the crouching chubby young man raises one palm out with a frown and "
     "says in Chinese: 「你敢说我胖？！」; the old fortune-teller gestures calmly beside him; "
     "the flat simple anime background stays unchanged; smooth limited TV-anime animation"),
    ("s5_stool", 195, "anime_ch1_s5_stool.png",
     "anime style 2D animation, cel-shaded: the old fortune-teller chants with fingers pinched: 「掌气起寒霜，六爷有痔疮。」; "
     "then the chubby young man furiously raises the small wooden stool high and swings it downward; "
     "the old fortune-teller crouching below flinches with hands over his face; "
     "the flat simple anime background stays unchanged; smooth limited TV-anime animation"),
]

for tag, seed, img, _ in SHOTS:
    src = f"{ROOT}/output/liulaoliu_story/sheets/{img}"
    shutil.copy(src, f"{INPUT_DIR}/{img}")
print("[prep] input images synced", flush=True)


def snap():
    return set(p.name for p in VIDEO_DIR.glob("*.mp4"))


def run_shot(tag, seed, img, prompt):
    dst = WORK / f"ep1_{tag}_line.mp4"
    if dst.exists():
        print(f"[skip] {tag} (exists)", flush=True)
        return
    base = json.load(open(WF_SRC))
    for n in base["nodes"]:
        if n.get("id") == 114:
            n["widgets_values"][0] = img
        if n.get("id") == 105:
            n["widgets_values"][0] = prompt
            n["widgets_values"][3] = 6
            n["widgets_values"][4] = seed
        if n.get("id") == 115 and isinstance(n["widgets_values"][0], str) \
                and n["widgets_values"][0].startswith("1:1"):
            n["widgets_values"][0] = "16:9 (Widescreen)"
    wf_path = f"{SCRATCH}/h3_ep1_{tag}_line.json"
    json.dump(base, open(wf_path, "w"), ensure_ascii=False, indent=1)

    before = snap()
    env = dict(os.environ)
    env["NO_PROXY"] = "127.0.0.1,localhost"
    env["COMFY_LOCAL_URL"] = "http://127.0.0.1:8199"
    t0 = time.time()
    r = subprocess.run(
        ["/home/zhaoyiming/.local/bin/comfy", "run", "--workflow", wf_path, "--wait"],
        env=env, capture_output=True, text=True, timeout=1800)
    out = r.stdout + r.stderr
    if r.returncode != 0 or '"ok": true' not in out:
        raise RuntimeError(f"{tag} comfy run failed: {out[-500:]}")
    new = snap() - before
    if not new:
        raise RuntimeError(f"{tag}: no new video found")
    shutil.copy(VIDEO_DIR / sorted(new)[-1], dst)
    print(f"[{tag}] seed={seed} {time.time()-t0:.1f}s -> {sorted(new)[-1]}", flush=True)


for tag, seed, img, prompt in SHOTS:
    run_shot(tag, seed, img, prompt)

print("ALL_DONE", flush=True)

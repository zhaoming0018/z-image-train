#!/usr/bin/env python3
"""第二章动漫集 · 6 镜 i2v（MiniMax H3，每镜 8 秒、H3 原生中文台词）。
幂等：已存在自动跳过；单镜重跑 = 删该镜 mp4 后重跑本脚本。
产出：WORK/ep2full_sN.mp4（WORK=/home/zhaoyiming/.hermes/cache/scratch/ep2）
"""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = "/home/zhaoyiming/z-image-train"
WORK = Path("/home/zhaoyiming/.hermes/cache/scratch/ep2")
WORK.mkdir(parents=True, exist_ok=True)
VIDEO_DIR = Path("/mnt/d/minimax-h3-demo/ComfyUI/output/video")
INPUT_DIR = "/mnt/d/minimax-h3-demo/ComfyUI/input"
SCRATCH = "/home/zhaoyiming/.hermes/cache/scratch"
WF_SRC = "/mnt/d/minimax-h3-demo/workflows/video_minimax_h3_i2v.json"

SHOTS = [
    ("s1_sign", 301, "anime_ch2_s1_sign.png",
     "anime style 2D animation, cel-shaded: a single person in the scene, only one young man, no one else — "
     "the chubby young man in the white tank top looks up at the 「北台肥羊」 signboard of the old hotpot restaurant, "
     "gives a cynical shrug, then walks in, muttering to himself in Chinese: 「富老大就安排这地方吃饭？」; "
     "then he adds under his breath: 「办完事还得回去揍他一顿。」; the flat simple anime street background stays "
     "unchanged; smooth limited TV-anime animation"),
    ("s2_frontdesk", 307, "anime_ch2_s2_frontdesk.png",
     "anime style 2D animation, cel-shaded: exactly two people, no duplicates — the chubby young man walks in "
     "through the steamy entrance of the hotpot restaurant and STAYS in the frame facing the counter; the plump "
     "waitress in the pink uniform behind the front counter greets him sweetly in Chinese: 「六哥来啦~」; "
     "the young man snaps back: 「叫什么叫！六爷办正事儿呢。」; the young man never leaves the frame; "
     "the flat simple anime interior stays unchanged; smooth limited TV-anime animation"),
    ("s3_manager", 303, "anime_ch2_s3_manager.png",
     "anime style 2D animation, cel-shaded: the middle-aged manager in the dark vest leans in and says with a sly "
     "grin in Chinese: 「老六来啦？富老大在楼上 203。」; the chubby young man blinks in surprise: 「楼上？203？」; "
     "exactly two people in focus, no duplicates; the flat simple anime interior stays unchanged; smooth limited "
     "TV-anime animation"),
    ("s4_slam", 304, "anime_ch2_s4_slam.png",
     "anime style 2D animation, cel-shaded: exactly two people, no duplicates — the stocky middle-aged man at the "
     "head of the round table slams the table and yells furiously in Chinese: 「你个小崽子是想让我丢人啊？！」; "
     "the chubby young man beside him bows with a fawning apologetic smile: 「我错了，我错了，老大你消消气。」; "
     "the flat simple anime interior stays unchanged; smooth limited TV-anime animation"),
    ("s5_flee", 308, "anime_ch2_s5_flee.png",
     "anime style 2D animation, cel-shaded: the chubby young man keeps hurrying toward the door in continuous "
     "motion, body leaning forward, never stopping, slipping a pack of cigarettes into his pocket; from behind him "
     "the stocky old man's furious voice yells in Chinese: 「刘老六！！他妈的我烟呢，是不是又让你顺跑了！！！」; "
     "the stocky man stays seated small in the blurred background, the young man remains the clear subject; "
     "the flat simple anime interior stays unchanged; smooth limited TV-anime animation"),
    ("s6_netbar", 306, "anime_ch2_s6_netbar.png",
     "anime style 2D animation, cel-shaded: exactly two people, no duplicates — the skinny young man standing on "
     "the chair yells in Chinese: 「谁他妈扔的闪光？！」; the chubby young man kicks the chair from below and snaps: "
     "「叫毛呢！」; the skinny man hops down with a grin: 「哎呦，六哥！」; the flat simple anime interior stays "
     "unchanged; smooth limited TV-anime animation"),
]

for tag, seed, img, _ in SHOTS:
    src = f"{ROOT}/output/liulaoliu_story/sheets/{img}"
    shutil.copy(src, f"{INPUT_DIR}/{img}")
print("[prep] input images synced", flush=True)


def snap():
    return set(p.name for p in VIDEO_DIR.glob("*.mp4"))


def run_shot(tag, seed, img, prompt):
    dst = WORK / f"ep2full_{tag}.mp4"
    if dst.exists():
        print(f"[skip] {tag} (exists)", flush=True)
        return
    base = json.load(open(WF_SRC))
    for n in base["nodes"]:
        if n.get("id") == 114:
            n["widgets_values"][0] = img
        if n.get("id") == 105:
            n["widgets_values"][0] = prompt
            n["widgets_values"][3] = 8
            n["widgets_values"][4] = seed
        if n.get("id") == 115 and isinstance(n["widgets_values"][0], str) \
                and n["widgets_values"][0].startswith("1:1"):
            n["widgets_values"][0] = "16:9 (Widescreen)"
    wf_path = f"{SCRATCH}/h3_ep2full_{tag}.json"
    json.dump(base, open(wf_path, "w"), ensure_ascii=False, indent=1)

    before = snap()
    env = dict(os.environ)
    env["NO_PROXY"] = "127.0.0.1,localhost"
    env["COMFY_LOCAL_URL"] = "http://127.0.0.1:8199"
    t0 = time.time()
    r = subprocess.run(
        ["/home/zhaoyiming/.local/bin/comfy", "run", "--workflow", wf_path, "--wait"],
        env=env, capture_output=True, text=True, timeout=2400)
    out = r.stdout + r.stderr
    if r.returncode != 0 or '"ok": true' not in out:
        raise RuntimeError(f"{tag} comfy run failed: {out[-500:]}")
    new = snap() - before
    if not new:
        raise RuntimeError(f"{tag}: no new video found")
    shutil.copy(VIDEO_DIR / sorted(new)[-1], dst)
    print(f"[{tag}] seed={seed} dur=8 {time.time()-t0:.1f}s -> {sorted(new)[-1]}", flush=True)


for tag, seed, img, prompt in SHOTS:
    run_shot(tag, seed, img, prompt)

print("ALL_DONE", flush=True)

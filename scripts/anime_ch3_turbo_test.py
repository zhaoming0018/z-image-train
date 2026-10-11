#!/usr/bin/env python3
"""s02_walk Turbo 实验：同 seed 802、15s，turbo_mode=True（8 步蒸馏）。
对比 baseline（27.6 分钟/镜）。跑完打印耗时，产物落 scratch/ep3/ep3_s02_walk_TURBO.mp4"""
import json
import os
import shutil
import subprocess
import time

SCRATCH = "/home/zhaoyiming/.hermes/cache/scratch"
WORK = f"{SCRATCH}/ep3"
WF_SRC = "/mnt/d/minimax-h3-demo/workflows/video_minimax_h3_i2v.json"
VIDEO_DIR = "/mnt/d/minimax-h3-demo/ComfyUI/output/video"

IMG = "anime_ch3src_s02_walk.png"
PROMPT = ("anime style 2D animation, cel-shaded: the characters speak ONLY the exact quoted Chinese lines, word for "
          "word, no improvised extra words; two young men hurry down an old small-town street — clearly ON the "
          "street, with shuttered shops and signs on both sides behind them: the chubby young man from the FIRST "
          "reference image walks briskly pulling the skinny shabby-suit young man from the SECOND reference image "
          "along by the arm, both walking with urgency; exactly two people in the whole scene, no duplicates; flat "
          "simple anime background stays unchanged; smooth limited TV-anime animation")
SEED = 802
DUR = 15

wf = json.load(open(WF_SRC))
for n in wf["nodes"]:
    if n.get("id") == 114:
        n["widgets_values"][0] = IMG
    if n.get("id") == 105:
        wv = n["widgets_values"]
        wv[0] = PROMPT
        wv[3] = DUR
        wv[4] = SEED
        wv[9] = True   # turbo_mode = ON
        wv[12] = 8     # turbo steps
        print("node105 widgets tail:", json.dumps(wv[9:], ensure_ascii=False), flush=True)
json.dump(wf, open(f"{SCRATCH}/h3_s02_turbo.json", "w"), ensure_ascii=False, indent=1)

before = set(os.listdir(VIDEO_DIR))
env = dict(os.environ)
env["NO_PROXY"] = "127.0.0.1,localhost"
env["COMFY_LOCAL_URL"] = "http://127.0.0.1:8199"
t0 = time.time()
r = subprocess.run(["/home/zhaoyiming/.local/bin/comfy", "run", "--workflow", f"{SCRATCH}/h3_s02_turbo.json",
                    "--wait", "--timeout", "3600"], env=env, capture_output=True, text=True, timeout=3600)
out = r.stdout + r.stderr
elapsed = time.time() - t0
print(f"exit={r.returncode} elapsed={elapsed:.0f}s ({elapsed/60:.1f} min)", flush=True)
if r.returncode != 0 or '"ok": true' not in out:
    print(out[-800:])
    raise SystemExit(1)
new = set(os.listdir(VIDEO_DIR)) - before
vid = sorted(new)[-1]
shutil.copy(f"{VIDEO_DIR}/{vid}", f"{WORK}/ep3_s02_walk_TURBO.mp4")
print(f"TURBO_DONE {vid} -> ep3_s02_walk_TURBO.mp4 in {elapsed:.0f}s", flush=True)

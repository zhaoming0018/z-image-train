#!/usr/bin/env python3
"""第三章试片 · 5秒动作镜头（seedance 风格 prompt：分时段+运镜+音效）。
产出：scratch/ch3test_fist_5s.mp4
"""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

SCRATCH = "/home/zhaoyiming/.hermes/cache/scratch"
WORK = Path(f"{SCRATCH}/ch3test")
WORK.mkdir(parents=True, exist_ok=True)
VIDEO_DIR = Path("/mnt/d/minimax-h3-demo/ComfyUI/output/video")
INPUT_DIR = "/mnt/d/minimax-h3-demo/ComfyUI/input"
WF_SRC = "/mnt/d/minimax-h3-demo/workflows/video_minimax_h3_i2v.json"
IMG = "anime_ch3test_fist.png"
DUR = 5
SEED = 701

PROMPT = (
    "anime style 2D animation, cel-shaded, Japanese TV anime: a wrecked old restaurant private room, low camera "
    "angle — a bald fat boss in a white undershirt with a shiny bald head and thick stubble crouches low on the "
    "floor and swings a big Chinese watermelon knife upward toward the chubby young man with short black hair in "
    "the white tank top; the young man ducks low and smashes his fist straight down onto the blade — the knife "
    "bends and flies out of the bald man's hand; then slow push-in: the bald boss stares dumbfounded, the young "
    "man looks stunned at his own fist; the two men look clearly different — the young man is young with a round "
    "face and hair, the boss is bald, much older; "
    "camera: low-angle shot, slight camera shake at the impact moment, slow push-in at the end; "
    "sound: knife whoosh, loud metal clang, tinkling broken glass, noisy brawl room ambience; "
    "exactly two people, no duplicates; "
    "flat simple anime background stays unchanged; smooth limited TV-anime animation"
)

shutil.copy(f"/home/zhaoyiming/z-image-train/output/liulaoliu_story/sheets/{IMG}", f"{INPUT_DIR}/{IMG}")

base = json.load(open(WF_SRC))
for n in base["nodes"]:
    if n.get("id") == 114:
        n["widgets_values"][0] = IMG
    if n.get("id") == 105:
        n["widgets_values"][0] = PROMPT
        n["widgets_values"][3] = DUR
        n["widgets_values"][4] = SEED
    if n.get("id") == 115 and isinstance(n["widgets_values"][0], str) \
            and n["widgets_values"][0].startswith("1:1"):
        n["widgets_values"][0] = "16:9 (Widescreen)"
wf_path = f"{SCRATCH}/h3_ch3test_5s.json"
json.dump(base, open(wf_path, "w"), ensure_ascii=False, indent=1)

before = set(p.name for p in VIDEO_DIR.glob("*.mp4"))
env = dict(os.environ)
env["NO_PROXY"] = "127.0.0.1,localhost"
env["COMFY_LOCAL_URL"] = "http://127.0.0.1:8199"
t0 = time.time()
r = subprocess.run(["/home/zhaoyiming/.local/bin/comfy", "run", "--workflow", wf_path, "--wait", "--timeout", "3600"],
                   env=env, capture_output=True, text=True, timeout=3600)
out = r.stdout + r.stderr
if r.returncode != 0 or '"ok": true' not in out:
    raise RuntimeError(f"comfy run failed: {out[-500:]}")
new = set(p.name for p in VIDEO_DIR.glob("*.mp4")) - before
if not new:
    raise RuntimeError("no new video found")
shutil.copy(VIDEO_DIR / sorted(new)[-1], WORK / "ch3test_fist_5s.mp4")
print(f"[ch3test] dur={DUR} seed={SEED} {time.time()-t0:.1f}s -> {sorted(new)[-1]}", flush=True)
print("DONE", flush=True)

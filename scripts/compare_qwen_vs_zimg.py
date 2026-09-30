#!/usr/bin/env python3
"""模型对比测试：Qwen-Image 2.1 vs Z-Image Turbo（基座对比，均不挂 LoRA）

从项目场景 yaml 读取 prompt（占位符用 illustration.yaml 的块替换），
同 seed 分别提交到 ComfyUI（经桥接 8199），收图到 output/model_compare/。

用法：~/miniconda3/envs/aitk/bin/python3 compare_qwen_vs_zimg.py
"""
import json
import os
import re
import shutil
import time
import urllib.request
from copy import deepcopy

import yaml

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)

ROOT = "/home/zhaoyiming/z-image-train"
BRIDGE = "http://127.0.0.1:8199"
COMFY_OUT = "/mnt/d/minimax-h3-demo/ComfyUI/output"
DEST = f"{ROOT}/output/model_compare"

with open(f"{ROOT}/config/illustration.yaml") as f:
    blocks = yaml.safe_load(f)["blocks"]


def fill(t):
    return re.sub(r"\{(\w+)\}", lambda m: blocks[m.group(1)], t)


SCENES = [
    ("ch15", "s2_drive"),
    ("ch13", "s3_poster"),
    ("ch11", "s5_hug"),
]

qwen_tpl = json.load(open(f"{ROOT}/config/qwen21_api.json"))
zimg_tpl = json.load(open(f"{ROOT}/config/z_image_api.json"))


def submit(wf):
    body = json.dumps({"prompt": wf}).encode()
    req = urllib.request.Request(BRIDGE + "/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))["prompt_id"]


def wait_done(pid, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        with urllib.request.urlopen(f"{BRIDGE}/history/{pid}", timeout=30) as r:
            h = json.load(r)
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "error":
                return h[pid]
        time.sleep(3)
    raise TimeoutError(f"timeout waiting {pid}")


os.makedirs(DEST, exist_ok=True)
report = []

for chapter, scene_name in SCENES:
    y = yaml.safe_load(open(f"{ROOT}/config/scenes/{chapter}.yaml"))
    sc = next(s for s in y["scenes"] if s["name"] == scene_name)
    prompt = fill(sc["prompt"])
    seed = sc["seed"]

    runs = [
        ("qwen", qwen_tpl, "4", "prompt", "6", f"qwen21_cmp_{chapter}_{scene_name}"),
        ("zimg", zimg_tpl, "27", "text", "3", f"zimg_cmp_{chapter}_{scene_name}"),
    ]
    for model, tpl, pnode, pkey, snode, prefix in runs:
        wf = deepcopy(tpl)
        wf[pnode]["inputs"][pkey] = prompt
        wf[snode]["inputs"]["seed"] = seed
        wf["9"]["inputs"]["filename_prefix"] = prefix
        t0 = time.time()
        pid = submit(wf)
        res = wait_done(pid)
        dt = time.time() - t0
        outs = []
        for node_out in res.get("outputs", {}).values():
            for img in node_out.get("images", []):
                src = os.path.join(COMFY_OUT, img.get("subfolder", ""), img["filename"])
                dst = os.path.join(DEST, f"{model}_{chapter}_{scene_name}.png")
                if os.path.exists(src):
                    shutil.copy(src, dst)
                    outs.append(dst)
        line = f"{model:4s} {chapter} {scene_name:10s} seed={seed} {dt:6.1f}s -> {outs}"
        print(line, flush=True)
        report.append(line)

print("ALL_DONE", flush=True)
for r in report:
    print(r, flush=True)

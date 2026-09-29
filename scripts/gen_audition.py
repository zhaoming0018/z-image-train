#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""定妆候选批量生成（代码与数据分离：集合规格在 config/auditions/<集合名>.yaml）。
用法（CLI 基于 typer）：
      cd ~/z-image-train && unset HTTP_PROXY HTTPS_PROXY ALL_PROXY; export NO_PROXY=127.0.0.1,localhost
      python3 -u scripts/gen_audition.py [集合名 ...]   # 例：fu6lao / huiming / huiming_bare；缺省=全部
输出：~/z-image-train/output/liulaoliu_story/audition/<集合>/  + _manifest.json（幂等：已有文件自动跳过）
说明：候选图用于「用户确认定妆 → 转正为训练数据集」（build_dataset.py）；caption 在数据集阶段再生成。
日志: loguru → stderr（SKIP/OK/错误/进度）。
"""
import json, time, shutil, urllib.request, os
from glob import glob
from typing import Annotated, Optional

import typer
import yaml

from zlog import logger, setup_logging

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE = "http://127.0.0.1:8199"
OUT_DIR = "/mnt/d/minimax-h3-demo/ComfyUI/output"
BASE = os.path.join(ROOT, "output/liulaoliu_story/audition")
SPEC_DIR = os.path.join(ROOT, "config/auditions")
WF_PATH = os.path.join(ROOT, "config/z_image_api.json")

app = typer.Typer(add_completion=False, help="定妆候选批量生成（幂等；规格来自 config/auditions/*.yaml）")


def load_specs():
    specs = {}
    for path in sorted(glob(os.path.join(SPEC_DIR, "*.yaml"))):
        with open(path, encoding="utf-8") as f:
            specs[os.path.splitext(os.path.basename(path))[0]] = yaml.safe_load(f)
    return specs


def compose(spec):
    """规格 → (name, seed, prompt) 列表（{appearance} / {style} 占位替换）。"""
    return [(p["name"], p["seed"],
             p["prompt"].format(appearance=spec["appearance"], style=spec["style"]))
            for p in spec["prompts"]]


def req(url, data=None):
    r = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None,
                               headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode())

def run_set(tag, spec):
    d = os.path.join(BASE, tag)
    os.makedirs(d, exist_ok=True)
    manifest = []
    ok = 0
    items = compose(spec)
    for name, seed, prompt in items:
        dst = os.path.join(d, f"{tag}_{name}.png")
        if os.path.exists(dst) and os.path.getsize(dst) > 10000:
            logger.info(f"[{tag}/{name}] SKIP (exists)"); ok += 1; continue
        wf = json.load(open(WF_PATH))
        wf["27"]["inputs"]["text"] = prompt
        wf["3"]["inputs"]["seed"] = seed
        try:
            resp = req(f"{BRIDGE}/prompt", {"prompt": wf, "client_id": f"audition-{tag}"})
            pid = resp.get("prompt_id")
            if not pid:
                logger.error(f"[{tag}/{name}] SUBMIT FAIL {json.dumps(resp)[:200]}")
                continue
            t0 = time.time()
            while time.time() - t0 < 240:
                time.sleep(2)
                h = req(f"{BRIDGE}/history/{pid}")
                if pid in h and h[pid].get("outputs"):
                    f0 = h[pid]["outputs"]["9"]["images"][0]
                    src = os.path.join(OUT_DIR, f0.get("subfolder", ""), f0["filename"])
                    shutil.copyfile(src, dst)
                    manifest.append({"file": f"{tag}_{name}.png", "seed": seed, "prompt": prompt})
                    logger.info(f"[{tag}/{name}] OK {time.time()-t0:.0f}s")
                    ok += 1
                    break
            else:
                logger.error(f"[{tag}/{name}] TIMEOUT")
        except Exception as e:
            logger.error(f"[{tag}/{name}] ERROR {e}")
    mf = os.path.join(d, "_manifest.json")
    prev = json.load(open(mf)) if os.path.exists(mf) else []
    keep = {m["file"] for m in prev}
    if not manifest:
        manifest = prev
    else:
        manifest = prev + [m for m in manifest if m["file"] not in keep]
    with open(mf, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    logger.success(f"[{tag}] DONE {ok}/{len(items)}")


@app.command()
def main(
    sets: Annotated[Optional[list[str]], typer.Argument(help="集合名（如 fu6lao / huiming_bare）；缺省=config/auditions/ 全部")] = None,
):
    """批量生成定妆候选（幂等：已有文件自动跳过；规格见 config/auditions/）。"""
    setup_logging()
    specs = load_specs()
    for tag in sets or sorted(specs):
        if tag not in specs:
            logger.warning(f"未知集合: {tag}")
            continue
        run_set(tag, specs[tag])
    logger.success("AUDITION DONE")


if __name__ == "__main__":
    app()

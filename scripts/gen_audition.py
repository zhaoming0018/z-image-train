#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""定妆候选批量生成（代码与数据分离：集合规格在 config/auditions/<集合名>.yaml）。
用法（CLI 基于 typer）: python3 -u scripts/gen_audition.py [集合名 ...]   # 例：fu6lao / huiming / huiming_bare；缺省=全部
输出：output/liulaoliu_story/audition/<集合>/  + _manifest.json（幂等：已有文件自动跳过）
说明：候选图用于「用户确认定妆 → 转正为训练数据集」（build_dataset.py）；caption 在数据集阶段再生成。
日志: loguru → stderr（SKIP/OK/错误/进度）。ComfyUI 调用走 comfy_lib（自动绕环境代理，无需再 unset 代理变量）。
"""
import json
from typing import Annotated, Optional

import typer

from comfy_lib import build_workflow, render
from zconf import CONFIG_DIR, ROOT, load_specs
from zlog import logger, setup_logging

BASE = ROOT / "output/liulaoliu_story/audition"
WF_PATH = CONFIG_DIR / "z_image_api.json"

app = typer.Typer(add_completion=False, help="定妆候选批量生成（幂等；规格来自 config/auditions/*.yaml）")


def compose(spec):
    """规格 → (name, seed, prompt) 列表（{appearance} / {style} 占位替换）。"""
    return [(p["name"], p["seed"],
             p["prompt"].format(appearance=spec["appearance"], style=spec["style"]))
            for p in spec["prompts"]]


def _merge_manifest(prev, new):
    """合并候选记录：同文件名以新记录为准（回炉重拍更新 seed/提示词），新文件追加、顺序稳定。"""
    by_file = {m["file"]: m for m in new}
    merged = [by_file.pop(m["file"], m) for m in prev]
    merged += list(by_file.values())
    return merged


def run_set(tag, spec):
    d = BASE / tag
    d.mkdir(parents=True, exist_ok=True)
    manifest = []
    ok = 0
    items = compose(spec)
    for name, seed, prompt in items:
        dst = d / f"{tag}_{name}.png"
        if dst.exists() and dst.stat().st_size > 10000:
            logger.info(f"[{tag}/{name}] SKIP (exists)"); ok += 1; continue
        try:
            wf = build_workflow(WF_PATH, prompt, seed)
            res = render(wf, dst, f"audition-{tag}", poll_timeout=240.0)
            if not res["ok"]:
                logger.error(f"[{tag}/{name}] {res['error']}")
                continue
            manifest.append({"file": f"{tag}_{name}.png", "seed": seed, "prompt": prompt})
            logger.info(f"[{tag}/{name}] OK {res['seconds']:.0f}s")
            ok += 1
        except Exception as e:  # noqa: BLE001
            logger.error(f"[{tag}/{name}] ERROR {e}")
    mf = d / "_manifest.json"
    prev = json.load(open(mf)) if mf.exists() else []
    manifest = _merge_manifest(prev, manifest) if manifest else prev
    with open(mf, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    logger.success(f"[{tag}] DONE {ok}/{len(items)}")


@app.command()
def main(
    sets: Annotated[Optional[list[str]], typer.Argument(help="集合名（如 fu6lao / huiming_bare）；缺省=config/auditions/ 全部")] = None,
):
    """批量生成定妆候选（幂等：已有文件自动跳过；规格见 config/auditions/）。"""
    setup_logging()
    specs = load_specs("auditions")
    for tag in sets or sorted(specs):
        if tag not in specs:
            logger.warning(f"未知集合: {tag}")
            continue
        run_set(tag, specs[tag])
    logger.success("AUDITION DONE")


if __name__ == "__main__":
    app()

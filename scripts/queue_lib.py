#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""z-image 出图队列公共库：配置加载 / 任务构建 / Redis 队列原语 / 渲染执行
日志：loguru（由调用方 setup_logging 配置；未配置时 loguru 默认 sink 仍可用）。
ComfyUI 调用（请求 / 工作流拼装 / 提交-轮询-取图）统一走 comfy_lib（全仓库唯一实现）。
"""
import json
import os
import time

from comfy_lib import build_workflow, render
from zconf import CONFIG_DIR, load_yaml
from zlog import logger

PENDING = "zimage:queue:pending"
PROCESSING = "zimage:queue:processing"
DONE = "zimage:queue:done"
FAILED = "zimage:queue:failed"
DONE_KEEP = 500


class ConfigError(Exception):
    pass


def now_str():
    return time.strftime("%m-%d %H:%M:%S")


# ---------- 配置 ----------

def load_global():
    return load_yaml(os.path.join(CONFIG_DIR, "illustration.yaml"))


def load_chapter(ch):
    p = os.path.join(CONFIG_DIR, "scenes", f"ch{ch}.yaml")
    if not os.path.exists(p):
        raise ConfigError(f"章节配置不存在: {p}")
    return load_yaml(p)


def resolve_prompt(template, blocks):
    try:
        return template.format_map(blocks)
    except KeyError as e:
        raise ConfigError(f"prompt 占位符未在 illustration.yaml blocks 中定义: {e}")


def build_jobs(global_cfg, chapter_cfgs, only=None, suffix="", seed=None, force=False):
    """章节配置 → (待入队任务列表, 已存在跳过列表)。"""
    jobs, skipped = [], []
    story_root = global_cfg["story_root"]
    strength = global_cfg["render"]["strength"]
    for doc in chapter_cfgs:
        ch = doc["chapter"]
        for sc in doc["scenes"]:
            name = sc["name"]
            if only and name not in only:
                continue
            sd = seed if seed is not None else sc.get("seed", 0)
            loras = []
            for lk in sc.get("loras", []):
                fn = global_cfg["loras"].get(lk)
                if not fn:
                    raise ConfigError(f"LoRA 未注册: {lk}（scene ch{ch}/{name}）")
                loras.append({"lora": fn, "strength": strength})
            out_dir = os.path.join(story_root, f"ch{ch}")
            out_path = os.path.join(out_dir, f"z_image_ch{ch}_{name}{suffix}.png")
            job = {
                "job_id": f"ch{ch}-{name}{suffix}-seed{sd}",
                "chapter": ch, "scene": name, "seed": sd, "suffix": suffix,
                "prompt": resolve_prompt(sc["prompt"], global_cfg["blocks"]),
                "loras": loras, "out_path": out_path, "force": bool(force),
            }
            if os.path.exists(out_path) and not force:
                skipped.append(job)
            else:
                jobs.append(job)
    return jobs, skipped


# ---------- Redis 队列原语 ----------

def get_redis(cfg):
    try:
        import redis
    except ImportError:
        raise SystemExit("缺少 python3-redis：sudo apt install python3-redis（并用 /usr/bin/python3 运行）")
    r = cfg["redis"]
    return redis.Redis(host=r["host"], port=r["port"], db=r.get("db", 0), decode_responses=True)


def enqueue(r, jobs):
    n = 0
    for j in jobs:
        r.rpush(PENDING, json.dumps(j, ensure_ascii=False))
        n += 1
    return n


def claim(r, timeout=5):
    """可靠领取：RPOPLPUSH → processing（worker 崩溃后由 requeue_processing 回收）"""
    return r.brpoplpush(PENDING, PROCESSING, timeout=timeout)


def finish(r, item, record):
    r.lrem(PROCESSING, 1, item)
    r.rpush(DONE, json.dumps(record, ensure_ascii=False))
    r.ltrim(DONE, -DONE_KEEP, -1)


def fail(r, item, record):
    logger.error(f"[FAIL] {record.get('job_id')}: {record.get('error')}")
    r.lrem(PROCESSING, 1, item)
    r.rpush(FAILED, json.dumps(record, ensure_ascii=False))


def requeue_processing(r):
    n = 0
    while True:
        item = r.rpoplpush(PROCESSING, PENDING)
        if item is None:
            break
        n += 1
    return n


# ---------- ComfyUI 渲染 ----------

def render_job(job, cfg, log=None):
    """执行单个渲染任务 → {'ok': True, 'dst', 'size', 'seconds'} 或 {'ok': False, 'error', ...}"""
    wf = build_workflow(cfg["workflow"], job["prompt"], job["seed"], job["loras"])
    rcfg = cfg["render"]
    return render(
        wf, job["out_path"], "zimage-queue",
        bridge=cfg["bridge"], out_dir=cfg["comfy_output_dir"],
        submit_retries=int(rcfg.get("submit_retries", 3)),
        poll_interval=float(rcfg.get("poll_interval_s", 2)),
        poll_timeout=float(rcfg.get("poll_timeout_s", 300)),
    )

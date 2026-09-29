#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""z-image 出图队列公共库：配置加载 / 任务构建 / Redis 队列原语 / ComfyUI 渲染执行
日志：loguru（由调用方 setup_logging 配置；未配置时 loguru 默认 sink 仍可用）。
"""
import json
import os
import shutil
import time
import urllib.request
import urllib.error

from zlog import logger

ROOT = os.path.expanduser("~/z-image-train")
CONFIG_DIR = os.path.join(ROOT, "config")

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
    try:
        import yaml
    except ImportError:
        raise SystemExit("缺少 yaml：请用 /usr/bin/python3 运行（系统 python3 已带 pyyaml）")
    p = os.path.join(CONFIG_DIR, "illustration.yaml")
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_chapter(ch):
    import yaml
    p = os.path.join(CONFIG_DIR, "scenes", f"ch{ch}.yaml")
    if not os.path.exists(p):
        raise ConfigError(f"章节配置不存在: {p}")
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


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

def _req(url, data=None, timeout=30):
    body = json.dumps(data).encode() if data is not None else None
    rq = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # 绕过环境代理
    with opener.open(rq, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def build_workflow(wf_path, prompt, seed, loras):
    with open(wf_path, encoding="utf-8") as f:
        wf = json.load(f)
    wf["27"]["inputs"]["text"] = prompt
    wf["3"]["inputs"]["seed"] = int(seed)
    if loras:
        prev = "28"
        for i, spec in enumerate(loras):
            nid = str(40 + i)
            wf[nid] = {
                "class_type": "LoraLoaderModelOnly",
                "inputs": {"model": [prev, 0], "lora_name": spec["lora"],
                           "strength_model": float(spec["strength"])},
            }
            prev = nid
        wf["11"]["inputs"]["model"] = [prev, 0]
    return wf


def render_job(job, cfg, log=None):
    """执行单个渲染任务 → {'ok': True, 'dst', 'size', 'seconds'} 或 {'ok': False, 'error', ...}"""
    t0 = time.time()
    bridge = cfg["bridge"]
    out_dir = cfg["comfy_output_dir"]
    rcfg = cfg["render"]
    wf = build_workflow(cfg["workflow"], job["prompt"], job["seed"], job["loras"])

    last_err, pid = "", None
    for _ in range(int(rcfg.get("submit_retries", 3))):
        try:
            resp = _req(f"{bridge}/prompt", {"prompt": wf, "client_id": "zimage-queue"})
            pid = resp.get("prompt_id")
            if pid:
                break
            last_err = json.dumps(resp, ensure_ascii=False)[:300]
        except urllib.error.HTTPError as e:
            try:
                last_err = f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}"
            except Exception:  # noqa: BLE001
                last_err = f"HTTP {e.code}"
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
        logger.debug(f"提交未成功，将重试: {last_err[:140]}")
        time.sleep(1.5)
    if not pid:
        return {"ok": False, "error": f"提交失败: {last_err}", "seconds": round(time.time() - t0, 1)}

    pi = float(rcfg.get("poll_interval_s", 2))
    pt = float(rcfg.get("poll_timeout_s", 300))
    while time.time() - t0 < pt:
        time.sleep(pi)
        try:
            h = _req(f"{bridge}/history/{pid}")
        except Exception:  # noqa: BLE001
            continue
        if pid in h and h[pid].get("outputs"):
            imgs = []
            for node in h[pid]["outputs"].values():
                imgs += node.get("images", [])
            if not imgs:
                return {"ok": False, "error": "history 无图像输出", "seconds": round(time.time() - t0, 1)}
            f0 = imgs[0]
            src = os.path.join(out_dir, f0.get("subfolder", ""), f0["filename"])
            dst = job["out_path"]
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            size = os.path.getsize(dst)
            if size <= 0:
                return {"ok": False, "error": "输出文件为空", "seconds": round(time.time() - t0, 1)}
            return {"ok": True, "dst": dst, "size": size,
                    "seconds": round(time.time() - t0, 1), "prompt_id": pid}
    return {"ok": False, "error": f"轮询超时 {pt:.0f}s", "seconds": round(time.time() - t0, 1)}

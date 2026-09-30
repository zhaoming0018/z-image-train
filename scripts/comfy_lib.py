#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ComfyUI 桥接公共库：HTTP 原语 / 工作流拼装（含 LoRA 链）/ 提交-轮询-取图。

全仓库唯一实现（gen_audition / gen_with_lora / queue_lib 均由此调用）；HTTP 一律绕环境代理。
节点约定：27=CLIPTextEncode.text、3=KSampler.seed、28=主 UNet 源、11=采样器 model 入口、
LoRA 链节点 40+i（LoraLoaderModelOnly）、9=SaveImage。
用法:
    from comfy_lib import build_workflow, render
    wf = build_workflow(wf_path, prompt, seed, loras=[{"lora": fn, "strength": 0.9}])
    res = render(wf, dst, client_id)   # {'ok': True, 'dst', 'size', 'seconds', 'prompt_id'}
                                       # 或 {'ok': False, 'error', 'seconds'}
"""
import json
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

from zlog import logger

BRIDGE = "http://127.0.0.1:8199"  # Windows ComfyUI 认证桥（本机）
COMFY_OUT = "/mnt/d/minimax-h3-demo/ComfyUI/output"  # 桥后 ComfyUI 的输出目录（WSL 视角）


def req(url, data=None, timeout=30):
    """bridge JSON 请求（GET/POST 通用）；绕环境代理（WSL autoProxy 场景必需）。"""
    body = json.dumps(data).encode() if data is not None else None
    rq = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(rq, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def build_workflow(wf_path, prompt, seed, loras=None):
    """载入工作流 JSON → 注入 prompt/seed（可选 LoRA 链）→ 返回 dict。"""
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


def submit(bridge, wf, client_id, retries=1):
    """提交工作流 → (prompt_id | None, last_err)；失败按 retries 重试（间隔 1.5s）。"""
    last_err, pid = "", None
    for attempt in range(max(1, int(retries))):
        try:
            resp = req(f"{bridge}/prompt", {"prompt": wf, "client_id": client_id})
            pid = resp.get("prompt_id")
            if pid:
                return pid, ""
            last_err = json.dumps(resp, ensure_ascii=False)[:300]
        except urllib.error.HTTPError as e:
            try:
                last_err = f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}"
            except Exception:  # noqa: BLE001
                last_err = f"HTTP {e.code}"
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
        if attempt + 1 < int(retries):
            logger.debug(f"提交未成功，将重试: {last_err[:140]}")
            time.sleep(1.5)
    return None, last_err


def wait_result(bridge, pid, out_dir, poll_interval=2.0, poll_timeout=300.0):
    """轮询 /history 直到出图 → {'ok': True, 'src'}；超时/无图 → {'ok': False, 'error'}。"""
    t0 = time.time()
    while time.time() - t0 < poll_timeout:
        time.sleep(poll_interval)
        try:
            h = req(f"{bridge}/history/{pid}")
        except Exception:  # noqa: BLE001
            continue
        if pid in h and h[pid].get("outputs"):
            imgs = []
            for node in h[pid]["outputs"].values():
                imgs += node.get("images", [])
            if not imgs:
                return {"ok": False, "error": "history 无图像输出"}
            f0 = imgs[0]
            return {"ok": True, "src": Path(out_dir) / f0.get("subfolder", "") / f0["filename"]}
    return {"ok": False, "error": f"轮询超时 {poll_timeout:.0f}s"}


def render(wf, dst, client_id, bridge=BRIDGE, out_dir=COMFY_OUT,
           submit_retries=1, poll_interval=2.0, poll_timeout=300.0):
    """提交 → 轮询 → 拷回 dst。

    返回 {'ok': True, 'dst', 'size', 'seconds', 'prompt_id'}
      或 {'ok': False, 'error', 'seconds'}（提交失败/轮询超时/无图/空文件）。
    """
    t0 = time.time()
    pid, err = submit(bridge, wf, client_id, retries=submit_retries)
    if not pid:
        return {"ok": False, "error": f"提交失败: {err}", "seconds": round(time.time() - t0, 1)}
    r = wait_result(bridge, pid, out_dir, poll_interval=poll_interval, poll_timeout=poll_timeout)
    if not r["ok"]:
        return {"ok": False, "error": r["error"], "seconds": round(time.time() - t0, 1)}
    dst_path = Path(dst)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(r["src"], dst_path)
    size = dst_path.stat().st_size
    if size <= 0:
        return {"ok": False, "error": "输出文件为空", "seconds": round(time.time() - t0, 1)}
    return {"ok": True, "dst": dst, "size": size, "seconds": round(time.time() - t0, 1), "prompt_id": pid}

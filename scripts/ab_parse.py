#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析单个 A/B 实验的结果：稳定 s/it、步数、显存峰值(Prometheus)、墙钟、OOM/异常标志
输出单行: name=... ok=1 rc=0 steps_done=60 expect=60 steady_s_it=3.21 vram_peak_mb=12456 ...
显存峰值与墙钟时长均取自 <metrics-csv> 首末时间窗口 → 该窗口内查询 Prometheus（obs 栈）。
统计量计算走 numpy/scipy（步数-时间最小二乘回归 → s/it）。
CLI 基于 typer（`--help` 查看选项）；stdout 仅输出上述单行（被 ab_suite.sh 捕获）。
诊断信息走 loguru → stderr（ZLOG_LEVEL=DEBUG 可见细节）。
"""
import csv
import os
import re
import sys
from datetime import datetime, timedelta
from typing import Annotated

import numpy as np
import typer
from scipy.stats import linregress

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gpu_summary import gpu_summary  # 显存峰值：数据源 Prometheus
from zlog import logger, setup_logging

app = typer.Typer(add_completion=False, help="A/B 实验结果解析（单行输出）")


def _epoch(dt):
    """把「%m-%d %H:%M:%S」解析出的无年份 datetime 归到合理年份（当前年；若超前则回退一年）。"""
    now = datetime.now()
    try:
        cand = dt.replace(year=now.year)
    except ValueError:  # 2/29 边界
        cand = dt.replace(year=now.year, day=28)
    if cand > now + timedelta(days=1):
        cand = cand.replace(year=cand.year - 1)
    return int(cand.timestamp())


@app.command()
def main(
    log: Annotated[str, typer.Option("--log", help="训练日志路径")],
    name: Annotated[str, typer.Option("--name", help="实验名")],
    metrics_csv: Annotated[str, typer.Option("--metrics-csv", help="monitor 产出的 metrics csv")] = "",
    rc: Annotated[int, typer.Option("--rc", help="训练进程退出码")] = 0,
    expect: Annotated[int, typer.Option("--expect", help="期望步数（0=不校验）")] = 0,
):
    """解析日志 + metrics csv，输出单行结果摘要。"""
    setup_logging()
    out = {
        "name": name, "ok": 0, "rc": rc,
        "steps_done": 0, "expect": expect,
        "steady_s_it": "", "vram_peak_mb": "", "wall_min": "",
        "oom": 0, "err": 0, "loss_last": "",
    }

    # 1) 训练日志：步数 / OOM / 异常 / loss
    text = ""
    if os.path.exists(log):
        sz = os.path.getsize(log)
        with open(log, "r", errors="replace") as f:
            if sz > 3_000_000:
                f.seek(sz - 3_000_000)
            text = f.read()
    steps = [int(m[0]) for m in re.findall(r"(\d+)/(\d+) \[", text)]
    if steps:
        out["steps_done"] = int(np.max(steps))
    low = text.lower()
    out["oom"] = 1 if ("out of memory" in low or "outofmemoryerror" in low) else 0
    out["err"] = 1 if "traceback (most recent call last)" in low else 0
    m = re.findall(r"loss: ([0-9.eE+-]+)", text)
    if m:
        out["loss_last"] = m[-1]

    # 2) 稳定速度：对 (时间, 步数) 做最小二乘线性回归求斜率（step>=10 的尾段）
    pts = []
    if metrics_csv and os.path.exists(metrics_csv):
        with open(metrics_csv, newline="") as f:
            for row in csv.DictReader(f):
                try:
                    st = int(row.get("step") or 0)
                except ValueError:
                    continue
                if st <= 0:
                    continue
                try:
                    t0 = datetime.strptime(row.get("time") or "", "%m-%d %H:%M:%S")
                except ValueError:
                    continue
                pts.append((t0, st))
        if len(pts) >= 4:
            seen = {}
            for t0, st in pts:
                seen[t0.timestamp()] = st  # 同一秒保留最新
            xs = sorted(seen.keys())
            ys = [seen[x] for x in xs]
            sel = [(x, y) for x, y in zip(xs, ys) if y >= 10]
            if len(sel) >= 3:
                # 最小二乘回归（scipy）：斜率 = steps/s → s/it = 1/斜率
                x = np.array([t - sel[0][0] for t, _ in sel], dtype=float)
                y = np.array([s for _, s in sel], dtype=float)
                slope = linregress(x, y).slope
                if slope > 0:
                    out["steady_s_it"] = round(1.0 / slope, 2)

    # 3) GPU：显存峰值（Prometheus）+ 墙钟时长（窗口=metrics 首末时间）
    if pts:
        first_t, last_t = pts[0][0], pts[-1][0]
        out["wall_min"] = round((last_t - first_t).total_seconds() / 60.0, 1)
        try:
            s = gpu_summary(_epoch(first_t), _epoch(last_t))
            if s.get("mem_max_gib") is not None:
                out["vram_peak_mb"] = int(round(s["mem_max_gib"] * 1024))
        except Exception as e:  # noqa: BLE001
            logger.debug(f"gpu_summary 查询失败: {e}")

    out["ok"] = 1 if (
        rc == 0 and not out["oom"] and not out["err"]
        and (expect == 0 or out["steps_done"] >= expect)
    ) else 0

    order = ["name", "ok", "rc", "steps_done", "expect", "steady_s_it",
             "vram_peak_mb", "wall_min", "oom", "err", "loss_last"]
    print(" ".join(f"{k}={out[k]}" for k in order))


if __name__ == "__main__":
    app()

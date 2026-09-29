#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Z-Image LoRA 训练指标记录器
- GPU 汇总：训练结束时从 Prometheus 查询（obs 栈 nvidia_gpu_*，5s 采样；不再自采自写）
- 增量解析训练日志（loss/lr/速度）→ <prefix>_metrics.csv
- 关键事件 + 新样本图 → <prefix>_events.log
- 训练进程结束后生成 <prefix>_summary.txt（loss 极值等统计走 numpy）
用法（CLI 基于 typer）: python3 monitor_train.py --log LOG --prefix liu [--interval 30] [--proc-pattern "run.py .*config/train/"] [--samples-dir DIR]
日志: loguru → stderr（时间戳/级别）；摘要报告 → stdout + 文件
"""
import csv
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from typing import Annotated

import numpy as np
import typer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gpu_summary import gpu_summary, fmt_line  # GPU 汇总：数据源 Prometheus（obs 栈）
from zlog import logger, setup_logging  # 事件日志（stderr）

app = typer.Typer(add_completion=False, help="训练指标记录器（loss/lr/速度 → CSV，结束出摘要）")


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:
        return f"ERR:{e}"


@app.command()
def main(
    log: Annotated[str, typer.Option("--log", help="训练日志路径（监控目标）")],
    prefix: Annotated[str, typer.Option("--prefix", help="指标文件前缀（如 fu6lao）")],
    interval: Annotated[int, typer.Option("--interval", help="轮询间隔（秒）")] = 30,
    proc_pattern: Annotated[str, typer.Option("--proc-pattern", help="训练进程 pgrep 特征串")] = "run.py .*config/train/",
    samples_dir: Annotated[str, typer.Option("--samples-dir", help="样图目录（检测新样图事件）")] = "",
):
    """增量记录训练日志指标；训练进程消失后自动收尾出摘要。"""
    setup_logging()
    base = os.path.dirname(os.path.abspath(log))
    met_csv = os.path.join(base, f"{prefix}_metrics.csv")
    evt_log = os.path.join(base, f"{prefix}_events.log")
    sum_txt = os.path.join(base, f"{prefix}_summary.txt")

    with open(met_csv, "w", newline="") as f:
        csv.writer(f).writerow(["time", "step", "total", "loss", "lr", "speed", "raw"])

    def evt(msg):
        logger.info(msg)
        with open(evt_log, "a") as f:
            f.write(f"[{datetime.now().strftime('%m-%d %H:%M:%S')}] {msg}\n")

    evt(f"monitor start: log={log}")
    offset, gone_cnt = 0, 0
    losses, speeds = [], []
    seen_samples = 0
    start_t = datetime.now()

    step_re = re.compile(r"(?:step[:\s]*)?(\d+)\s*/\s*(\d+)")
    loss_re = re.compile(r"loss[=:\s]+([0-9]*\.?[0-9]+(?:e[+-]?\d+)?)", re.I)
    spd_re = re.compile(r"([0-9.]+)(it/s|s/it)")
    lr_re = re.compile(r"lr[=:\s]+([0-9.eE+-]+)")

    while True:
        # 日志增量解析
        try:
            size = os.path.getsize(log)
        except OSError:
            size = offset
        if size < offset:
            offset = 0
        if size > offset:
            with open(log, "r", errors="replace") as f:
                f.seek(offset)
                chunk = f.read()
                offset = f.tell()
            for ln in chunk.splitlines():
                if not ln.strip():
                    continue
                m = loss_re.search(ln)
                if m:
                    st = step_re.search(ln)
                    lr_m = lr_re.search(ln)
                    sp = spd_re.search(ln)
                    row = [datetime.now().strftime("%m-%d %H:%M:%S"),
                           st.group(1) if st else "", st.group(2) if st else "",
                           m.group(1), lr_m.group(1) if lr_m else "",
                           (sp.group(1) + sp.group(2)) if sp else "",
                           ln.strip()[:300]]
                    with open(met_csv, "a", newline="") as f:
                        csv.writer(f).writerow(row)
                    try:
                        losses.append((row[1], float(row[3])))
                    except ValueError:
                        pass
                    if row[5]:
                        speeds.append(row[5])
                low = ln.lower()
                for kw in ("saving", "complete", "quantiz", "cache", "error", "traceback", "out of memory", "sample"):
                    if kw in low and len(ln) < 400:
                        evt(ln.strip()[:220])
                        break

        # 新样本图检测
        if samples_dir and os.path.isdir(samples_dir):
            files = sorted(os.listdir(samples_dir))
            if len(files) > seen_samples:
                new = files[seen_samples:]
                seen_samples = len(files)
                evt("new samples: " + ", ".join(new[:8]))

        # 结束判定（排除监控器自身 PID：显式 --proc-pattern 会出现在自身命令行 → pgrep 假命中自己）
        pat = proc_pattern
        if pat:
            pat = f"[{pat[0]}]{pat[1:]}"  # 防自匹配：pgrep -f 会命中执行它的 shell 自身（其命令行含该串）
        out = sh(f"pgrep -f '{pat}'")
        pids = [p for p in out.split() if p.isdigit() and int(p) != os.getpid()]
        if pids:
            gone_cnt = 0
        else:
            gone_cnt += 1
            if gone_cnt >= 2:
                break
        time.sleep(interval)

    # 摘要
    end_t = datetime.now()
    lines = [f"=== {prefix} 训练指标摘要 ===",
             f"监测窗口: {start_t:%F %T} → {end_t:%F %T} (时长 {end_t - start_t})"]
    if losses:
        min_s, min_l = losses[int(np.argmin([l for _, l in losses]))]
        lines += [f"loss 采样点: {len(losses)}",
                  f"首: step {losses[0][0]} loss {losses[0][1]}",
                  f"末: step {losses[-1][0]} loss {losses[-1][1]}",
                  f"最低: step {min_s} loss {min_l}"]
    if speeds:
        lines.append(f"速度尾部样本: {speeds[-1]}（共 {len(speeds)}）")
    try:
        lines.append(fmt_line(gpu_summary(int(start_t.timestamp()), int(end_t.timestamp()))))
    except Exception as e:  # noqa: BLE001
        lines.append(f"GPU: 汇总不可用（{e}）")
    txt = "\n".join(lines)
    print(txt, flush=True)
    with open(sum_txt, "w") as f:
        f.write(txt + "\n")
    evt("monitor done")


if __name__ == "__main__":
    app()

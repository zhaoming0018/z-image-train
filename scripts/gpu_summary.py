#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GPU 指标汇总（数据源：obs 栈 Prometheus，nvidia_gpu_* 系列，5s 采样 / 15d 保留）

查询与解析走 prometheus-api-client（HTTP 请求构造 / 状态码检查 / 时间与数值解析全由库负责）；
统计聚合走 numpy（峰值/中位/均值；中位=标准中位数，偶数样本取中间两值均值）。
依赖：prometheus-api-client / numpy（系统 /usr/bin/python3 已装）。
用法（CLI 基于 typer，`--help` 查看全部选项）:
  python3 gpu_summary.py --start '2026-09-29 16:40' --end '2026-09-29 19:20'
  python3 gpu_summary.py --last 3h
  python3 gpu_summary.py --start ... --end ... --json
集成: from gpu_summary import gpu_summary, fmt_line
  gpu_summary(start_ts, end_ts) -> dict（Prometheus 不可达时返回 {'error': ...}）
"""
import json
import os
import time
from datetime import datetime
from typing import Annotated, Optional

import numpy as np
import requests
import typer
from prometheus_api_client import Metric, PrometheusConnect
from urllib3.util.retry import Retry

PROM_URL = os.environ.get("PROM_URL", "http://127.0.0.1:9090")
STEP_S = 15

app = typer.Typer(add_completion=False, help="GPU 指标汇总（数据源：obs 栈 Prometheus）")


def _connect():
    """PrometheusConnect：http + 不走环境代理（等价旧实现的 build_opener(ProxyHandler({}))）。

    超时拆为 (连接 3s, 读取 15s)；重试限界（total=2 / connect=1 / read=0 / 退避 0.5s）——
    本机（WSL）未监听端口表现为连接超时而非拒绝，库默认重试串上 15s 超时会拖到分钟级，
    限界后死端点数秒内降级返回。
    """
    session = requests.Session()
    session.trust_env = False
    retry = Retry(total=2, connect=1, read=0, backoff_factor=0.5,
                  status_forcelist=(408, 429, 500, 502, 503, 504))
    return PrometheusConnect(url=PROM_URL, disable_ssl=True, session=session,
                             retry=retry, timeout=(3, 15))


def _vals(pc, metric, start, end, step=STEP_S):
    """窗口内某指标的 (epoch, float) 采样点（升序）；查询/解析由 prometheus-api-client 完成。"""
    data = pc.custom_query_range(
        query=metric,
        start_time=datetime.fromtimestamp(start),
        end_time=datetime.fromtimestamp(end),
        step=f"{step}s",
    )
    pts = []
    for series in data:
        mv = Metric(series).metric_values  # DataFrame: ds=时间, y=数值（库已完成解析）
        for ds, y in mv.itertuples(index=False):
            pts.append((ds.timestamp(), float(y)))
    pts.sort()
    return pts


def gpu_summary(start, end, step=STEP_S):
    """start/end: unix 秒。返回汇总 dict；异常时 {'error': ...} 不抛。"""
    try:
        pc = _connect()
        mem = _vals(pc, "nvidia_gpu_memory_used_bytes", start, end, step)
        pw = _vals(pc, "nvidia_gpu_power_draw_watts", start, end, step)
        util = _vals(pc, "nvidia_gpu_utilization_percent", start, end, step)
        temp = _vals(pc, "nvidia_gpu_temperature_celsius", start, end, step)
    except Exception as e:  # noqa: BLE001 — 汇总场景要求降级不崩
        return {"error": str(e), "start": start, "end": end}
    if not mem:
        return {"error": "窗口内无采样", "start": start, "end": end}

    # 统计聚合走 numpy（中位=标准中位数，偶数样本取中间两值均值）
    def arr(xs):
        return np.array([v for _, v in xs], dtype=float)

    mem_v, pw_v = arr(mem), arr(pw)
    util_v, temp_v = arr(util), arr(temp)
    i_peak = int(mem_v.argmax())  # 峰值取样点（并列取最早，与旧实现一致）

    return {
        "mem_max_gib": round(float(mem_v.max()) / 2**30, 2),
        "mem_med_gib": round(float(np.median(mem_v)) / 2**30, 2),
        "mem_max_at": datetime.fromtimestamp(mem[i_peak][0]).strftime("%m-%d %H:%M:%S"),
        "power_max_w": round(float(pw_v.max())) if pw_v.size else None,
        "util_avg_pct": round(float(util_v.mean())) if util_v.size else None,
        "temp_max_c": round(float(temp_v.max())) if temp_v.size else None,
        "samples": int(mem_v.size),
        "start": start,
        "end": end,
    }


def fmt_line(s):
    if s.get("error"):
        return f"GPU: 汇总不可用（{s['error']}）"
    hhmmss = s["mem_max_at"].split(" ")[-1]
    return (f"GPU 峰值显存 {s['mem_max_gib']} GiB@{hhmmss}（中位 {s['mem_med_gib']} GiB）· "
            f"峰值功耗 {s['power_max_w']} W · 平均利用率 {s['util_avg_pct']}% · "
            f"最高温度 {s['temp_max_c']}°C · {s['samples']} 采样（源: Prometheus）")


def _parse_ts(s):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%H:%M"):
        try:
            dt = datetime.strptime(s, fmt)
            if fmt == "%H:%M":
                now = datetime.now()
                dt = dt.replace(year=now.year, month=now.month, day=now.day)
            return int(dt.timestamp())
        except ValueError:
            pass
    try:
        return int(float(s))
    except ValueError:
        typer.echo(f"无法解析时间: {s}", err=True)
        raise typer.Exit(1)


@app.command()
def main(
    start: Annotated[Optional[str], typer.Option("--start", help="起始时间：'YYYY-MM-DD HH:MM[:SS]' 或 'HH:MM'")] = None,
    end: Annotated[Optional[str], typer.Option("--end", help="结束时间（同 --start 格式）")] = None,
    last: Annotated[Optional[str], typer.Option("--last", help="回溯窗口，如 3h / 90m")] = None,
    step: Annotated[int, typer.Option("--step", help="Prometheus 查询步长（秒）")] = STEP_S,
    json_out: Annotated[bool, typer.Option("--json", help="以 JSON 输出汇总")] = False,
):
    """汇总指定时间窗内的 GPU 峰值/中位显存、功耗、利用率、温度。"""
    if last:
        n = last.strip().lower()
        if n.endswith("h"):
            secs = int(float(n[:-1]) * 3600)
        elif n.endswith("m"):
            secs = int(float(n[:-1]) * 60)
        else:
            typer.echo("--last 形如 3h / 90m", err=True)
            raise typer.Exit(1)
        t1 = int(time.time())
        t0 = t1 - secs
    elif start and end:
        t0, t1 = _parse_ts(start), _parse_ts(end)
    else:
        typer.echo("用法: --start+--end 或 --last 3h", err=True)
        raise typer.Exit(1)
    s = gpu_summary(t0, t1, step)
    if json_out:
        print(json.dumps(s, ensure_ascii=False, indent=1))
    else:
        print(fmt_line(s))


if __name__ == "__main__":
    app()

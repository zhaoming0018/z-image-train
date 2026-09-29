#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""z-image 出图队列 CLI（配置在 ~/z-image-train/config/，队列在 zimage-redis）

用法（CLI 基于 typer，`--help` 查看全部选项）:
  python3 queuectl.py enqueue 8 9 10                # 章节入队（已存在出图自动跳过）
  python3 queuectl.py enqueue 3 --only s2_chaos --suffix _v2 --seed 201   # 单景重拍
  python3 queuectl.py run 8 9                       # 入队 + 前台消费
  python3 queuectl.py worker [--idle-exit 300] [--max-jobs N]
  python3 queuectl.py status                        # 队列统计
  python3 queuectl.py retry-failed                  # 失败任务重新入队
  python3 queuectl.py purge pending|failed|all --yes
日志: worker 运行日志走 loguru → stderr（systemd 单元 append 到 logs/queue_worker.log）；
      enqueue/status/dry-run 等结果输出保持 stdout（print）。
"""
import json
import os
from enum import Enum
from typing import Annotated, Optional

import typer

import queue_lib as Q
from zlog import logger, setup_logging

app = typer.Typer(add_completion=False, help="z-image 出图队列 CLI（配置 config/，队列 zimage-redis）")


def _enqueue(chapters, only, suffix, seed, force, dry_run=False):
    cfg = Q.load_global()
    docs = [Q.load_chapter(ch) for ch in chapters]
    only_set = set(only.split(",")) if only else None
    jobs, skipped = Q.build_jobs(cfg, docs, only=only_set, suffix=suffix, seed=seed, force=force)
    for j in skipped:
        print(f"  跳过（已存在）: {j['job_id']}")
    if dry_run:
        for j in jobs:
            print(f"[dry-run] {j['job_id']} → {j['out_path']}")
        print(f"共 {len(jobs)} 个待入队（dry-run，未入队）")
        return cfg, None
    r = Q.get_redis(cfg)
    n = Q.enqueue(r, jobs)
    print(f"已入队 {n} 个任务（跳过 {len(skipped)} 个已存在）")
    return cfg, r


def _worker(cfg, r, idle_exit, max_jobs):
    setup_logging()
    recycled = Q.requeue_processing(r)
    if recycled:
        logger.warning(f"回收上次未完成任务 {recycled} 个（重新入队）")
    processed, idle = 0, 0
    logger.info(f"worker 启动（空闲 {idle_exit}s 自动退出 / --max-jobs {max_jobs or '∞'}）")
    try:
        while True:
            item = Q.claim(r, timeout=5)
            if item is None:
                idle += 5
                if idle_exit and idle >= idle_exit:
                    logger.info(f"队列为空已 {idle}s，退出。本批共处理 {processed} 个。")
                    break
                continue
            idle = 0
            job = json.loads(item)
            if not job.get("force") and os.path.exists(job["out_path"]):
                Q.finish(r, item, {"job_id": job["job_id"], "status": "skipped-exists",
                                   "ts": Q.now_str(), "out": job["out_path"]})
                logger.info(f"[skip] {job['job_id']}（已存在）")
                continue
            logger.info(f"[run ] {job['job_id']} …")
            res = Q.render_job(job, cfg)
            rec = {"job_id": job["job_id"], "ts": Q.now_str(), "out": job["out_path"], **res}
            if res.get("ok"):
                Q.finish(r, item, rec)
                logger.success(f"[done] {job['job_id']}  {res['seconds']}s  "
                               f"{res['size'] / 1e6:.1f}MB → {res['dst']}")
            else:
                Q.fail(r, item, rec)
            processed += 1
            if max_jobs and processed >= max_jobs:
                logger.info(f"达到 --max-jobs {max_jobs}，退出。")
                break
    except KeyboardInterrupt:
        logger.warning("已停止（processing 中任务将在下次启动时自动回收）")


def _status():
    cfg = Q.load_global()
    r = Q.get_redis(cfg)
    print(f"pending={r.llen(Q.PENDING)}  processing={r.llen(Q.PROCESSING)}  "
          f"done={r.llen(Q.DONE)}  failed={r.llen(Q.FAILED)}")
    for label, key in (("最近完成", Q.DONE), ("失败", Q.FAILED)):
        items = r.lrange(key, -8, -1)
        if items:
            print(f"-- {label}（末 {len(items)} 条）--")
            for it in items:
                try:
                    d = json.loads(it)
                    tail = d.get("error") or d.get("status") or f"{d.get('seconds', '')}s"
                    print("  ", d.get("ts"), d.get("job_id"), tail)
                except Exception:  # noqa: BLE001
                    print("  ", it[:120])


class PurgeTarget(str, Enum):
    pending = "pending"
    failed = "failed"
    all = "all"


@app.command()
def enqueue(
    chapters: Annotated[list[int], typer.Argument(help="章号，如 8 9 10")],
    only: Annotated[Optional[str], typer.Option("--only", help="只选指定场景（逗号分隔，如 s2_chaos,s5_slap）")] = None,
    suffix: Annotated[str, typer.Option("--suffix", help="输出文件名后缀（重拍用，如 _v2）")] = "",
    seed: Annotated[Optional[int], typer.Option("--seed", help="覆盖 seed（默认取场景配置）")] = None,
    force: Annotated[bool, typer.Option("--force", help="已存在也重出")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="只打印任务，不入队")] = False,
):
    """章节场景入队（已存在出图自动跳过）。"""
    _enqueue(chapters, only, suffix, seed, force, dry_run)


@app.command()
def run(
    chapters: Annotated[list[int], typer.Argument(help="章号，如 8 9 10")],
    only: Annotated[Optional[str], typer.Option("--only", help="只选指定场景（逗号分隔）")] = None,
    suffix: Annotated[str, typer.Option("--suffix", help="输出文件名后缀（重拍用，如 _v2）")] = "",
    seed: Annotated[Optional[int], typer.Option("--seed", help="覆盖 seed（默认取场景配置）")] = None,
    force: Annotated[bool, typer.Option("--force", help="已存在也重出")] = False,
    idle_exit: Annotated[int, typer.Option("--idle-exit", help="队列空 N 秒后自动退出")] = 300,
    max_jobs: Annotated[int, typer.Option("--max-jobs", help="最多处理 N 个（0=不限）")] = 0,
):
    """入队 + 前台消费。"""
    cfg, r = _enqueue(chapters, only, suffix, seed, force)
    if r is not None:
        _worker(cfg, r, idle_exit, max_jobs)


@app.command()
def worker(
    idle_exit: Annotated[int, typer.Option("--idle-exit", help="队列空 N 秒后自动退出")] = 300,
    max_jobs: Annotated[int, typer.Option("--max-jobs", help="最多处理 N 个（0=不限）")] = 0,
):
    """前台消费队列。"""
    cfg = Q.load_global()
    r = Q.get_redis(cfg)
    _worker(cfg, r, idle_exit, max_jobs)


@app.command()
def status():
    """队列统计（pending/processing/done/failed）。"""
    _status()


@app.command("retry-failed")
def retry_failed():
    """失败任务重新入队。"""
    cfg = Q.load_global()
    r = Q.get_redis(cfg)
    n = 0
    while True:
        item = r.lpop(Q.FAILED)
        if item is None:
            break
        r.rpush(Q.PENDING, item)
        n += 1
    print(f"已将 {n} 个失败任务重新入队")


@app.command()
def purge(
    what: Annotated[PurgeTarget, typer.Argument(help="清空范围")],
    yes: Annotated[bool, typer.Option("--yes", help="确认清空")] = False,
):
    """清空队列（pending / failed / all）。"""
    if not yes:
        typer.echo("purge 需要 --yes 确认", err=True)
        raise typer.Exit(1)
    cfg = Q.load_global()
    r = Q.get_redis(cfg)
    keys = {"pending": [Q.PENDING], "failed": [Q.FAILED],
            "all": [Q.PENDING, Q.PROCESSING, Q.FAILED, Q.DONE]}[what.value]
    for k in keys:
        r.delete(k)
    print("已清空:", ", ".join(keys))


if __name__ == "__main__":
    app()

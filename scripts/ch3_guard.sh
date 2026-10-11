#!/bin/bash
# 第三章视频批 · 带自愈守护：批脚本崩了自动续跑；ComfyUI 服务崩了自动重启。
# 用法: bash ch3_guard.sh [batch_py]
BATCH="${1:-/home/zhaoyiming/z-image-train/scripts/anime_ep3_batch.py}"
BRIDGE="http://127.0.0.1:8199"
PS1='D:\minimax-h3-demo\start-comfy-hidden.ps1'

check_health() {
  curl -s -m 8 --noproxy '*' "$BRIDGE/queue" | grep -q queue_running
}

for round in $(seq 1 40); do
  echo "[guard] round $round start $(date '+%H:%M:%S')"
  /usr/bin/python3 -u "$BATCH" && { echo "[guard] batch finished OK"; break; }
  echo "[guard] batch exited non-zero, checking service..."
  if ! check_health; then
    echo "[guard] service unhealthy -> restarting ComfyUI"
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$PS1" >/dev/null 2>&1 &
    sleep 120
  fi
  sleep 20
done
echo "[guard] done $(date '+%H:%M:%S')"

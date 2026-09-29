#!/bin/bash
# 串行训练链：多个配置逐个跑（单卡顺序执行，前一个失败则中断链路）
# 用法: bash scripts/train_chain.sh houshaolin_zimage.yaml tongyuhui_zimage.yaml
# 每个配置独立日志 logs/train_<slug>.log；链路状态追加到 logs/train_chain.status
set -u
LOG_DIR="$HOME/z-image-train/logs"
mkdir -p "$LOG_DIR"
STATUS="$LOG_DIR/train_chain.status"
for cfg in "$@"; do
  slug="${cfg%%_zimage.yaml}"
  echo "=== $cfg START $(date '+%F %T') ===" >> "$STATUS"
  bash "$HOME/z-image-train/run_train.sh" "$cfg" > "$LOG_DIR/train_${slug}.log" 2>&1
  rc=$?
  echo "=== $cfg END rc=$rc $(date '+%F %T') ===" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then
    echo "=== chain stop: $cfg rc=$rc $(date '+%F %T') ===" >> "$STATUS"
    break
  fi
  sleep 20
done
echo "=== chain done $(date '+%F %T') ===" >> "$STATUS"

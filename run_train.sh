#!/bin/bash
# Z-Image LoRA 训练启动器
# 用法: bash run_train.sh l6liu_zimage.yaml
# 功能: 释放 ComfyUI 占用的显存 → 启动 ai-toolkit 训练
#       训练配置在项目 config/train/（2026-09-29 从 ai-toolkit/config 迁出），以绝对路径传给 run.py
set -e
export HF_ENDPOINT=https://hf-mirror.com
export PATH="$HOME/.local/bin:$PATH"

PROJECT="$HOME/z-image-train"
CONFIG="$PROJECT/config/train/$1"

if [ ! -f "$CONFIG" ]; then
  echo "配置不存在: $CONFIG" >&2
  echo "可选: $(cd "$PROJECT/config/train" && ls *.yaml 2>/dev/null | tr '\n' ' ')" >&2
  exit 1
fi

echo "=== 释放 ComfyUI 显存 $(date '+%T') ==="
curl -s --noproxy '*' -X POST http://127.0.0.1:8199/free \
  -H "Content-Type: application/json" \
  -d '{"unload_models": true, "free_memory": true}' || true
sleep 3
nvidia-smi --query-gpu=memory.used --format=csv,noheader

cd "$PROJECT/ai-toolkit"
echo "=== 启动训练: $1 $(date '+%T') ==="
exec "$HOME/miniconda3/envs/aitk/bin/python" -u run.py "$CONFIG"

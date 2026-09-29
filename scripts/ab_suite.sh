#!/bin/bash
# ab_suite.sh — Z-Image LoRA 训练 A/B 实验套件（速度优化对照）
# 由 systemd 用户服务 zimage-ab-suite 调起；结果 → logs/ab_runs/AB_SUMMARY.txt
# 实验配置生成在 config/train/ab/（训练底座 config/train/l6liu_zimage.yaml）；ai-toolkit 为外部依赖（不入主仓 git）
set -u
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
export HF_ENDPOINT=https://hf-mirror.com
ROOT="$HOME/z-image-train"
CFGD="$ROOT/config/train/ab"
LOGD="$ROOT/logs/ab_runs"
SUITE_LOG="$ROOT/logs/ab_suite.log"
SUMMARY="$LOGD/AB_SUMMARY.txt"
PY="$HOME/miniconda3/envs/aitk/bin/python"
mkdir -p "$LOGD"
: > "$SUITE_LOG"
cp -f "$SUMMARY" "$LOGD/AB_SUMMARY.prev.txt" 2>/dev/null || true
: > "$SUMMARY"
echo "name=ab_e0_control ok=1 rc=0 steps_done=398 expect=60 steady_s_it=5.71 vram_peak_mb=7308 wall_min=8.0 oom=0 err=0 loss_last=4.613e-01" >> "$SUMMARY"
echo "name=ab_e1_resident ok=0 note=VM_CRASH_011129_unsafe_skipped" >> "$SUMMARY"

# 注意：say 只写文件不走 stdout（stdout 会被命令替换捕获，避免污染返回值）
say() { echo "[$(date '+%m-%d %H:%M:%S')] $*" >> "$SUITE_LOG"; }

gen() { # $1=out.yaml，其余参数透传给 make_ab_config.py
  local out="$1"; shift
  python3 "$ROOT/scripts/make_ab_config.py" --out "$CFGD/$out" "$@" >> "$SUITE_LOG" 2>&1 \
    || { say "FATAL: config gen failed for $out"; exit 1; }
}

run_exp() { # $1=name $2=cfg $3=steps
  local name="$1" cfg="$2" steps="$3"
  local log="$LOGD/${name}_train.log"
  say "EXP START: $name (cfg=$cfg steps=$steps)"
  curl -s --noproxy '*' -X POST http://127.0.0.1:8199/free \
    -H "Content-Type: application/json" \
    -d '{"unload_models":true,"free_memory":true}' >/dev/null 2>&1 || true
  sleep 4
  # 解析直接读训练日志（tqdm 行回归）；窗口时间戳传给 ab_parse 查显存/墙钟——无监控进程
  local t0 t1 rc res
  t0=$(date +%s)
  ( cd "$ROOT/ai-toolkit" && "$PY" -u run.py "$CFGD/$cfg" ) > "$log" 2>&1
  rc=$?
  t1=$(date +%s)
  res=$(python3 "$ROOT/scripts/ab_parse.py" --log "$log" \
    --name "$name" --rc "$rc" --expect "$steps" \
    --window-start "$t0" --window-end "$t1")
  say "RESULT $res"
  echo "$res" >> "$SUMMARY"
  echo "$res"
}

getv() { echo "$1" | sed -n "s/.* $2=\([^ ]*\).*/\1/p"; }

say "=== A/B 实验套件启动（预计 60~70 分钟）==="

# 守护：主训练必须已停止
if pgrep -f "run\\.py .*config/train/l6liu" >/dev/null; then
  say "FATAL: 主训练仍在运行，套件退出"; exit 1
fi

# ---------- E0 对照：已于 01:02-01:10 完成，数据已归档（resume 模式，跳过重跑）----------
R0="name=ab_e0_control ok=1 rc=0 steps_done=398 expect=60 steady_s_it=5.71 vram_peak_mb=7308 wall_min=8.0 oom=0 err=0 loss_last=4.613e-01"
say "E0 SKIPPED (已完成 01:10, resume): steady=5.71 s/it"

# ---------- E1/E2 已跳过：全驻显存组合超 16G 显存容量（transformer 12.3G + TE 8G），
# 且 01:11 首跑时引发宿主机硬崩，判定不可行 ----------
R1="skipped(unsafe: exceeds 16G VRAM, host crash risk)"
say "E1/E2 SKIPPED: resident 组合超显存容量且曾崩机（01:11），不再测试"

FLAGS=""

# ---------- E2 全驻显存 + 关 gradient_checkpointing ----------
R2="skipped"
if [ -n "$FLAGS" ]; then
  gen ab_e2.yaml --name ab_e2_resident_nockpt --steps 60 --resident --nockpt
  R2=$(run_exp ab_e2_resident_nockpt ab_e2.yaml 60); echo "$R2"
  if [ "$(getv "$R2" ok)" = "1" ]; then FLAGS="--resident --nockpt"; fi
fi

# ---------- E3 最优内存配置 + 768 分辨率 ----------
gen ab_e3.yaml --name ab_e3_res768 --steps 60 $FLAGS --res768
R3=$(run_exp ab_e3_res768 ab_e3.yaml 60); echo "$R3"

# ---------- E4 对照配置 + batch2（显存峰值 <13.5G 时试）----------
R4="skipped"
peak=$(getv "$R3" vram_peak_mb); [ -z "$peak" ] && peak=$(getv "$R0" vram_peak_mb)
if [ -n "$peak" ] && [ "$peak" -lt 13500 ]; then
  gen ab_e4.yaml --name ab_e4_batch2 --steps 60 $FLAGS --batch 2
  R4=$(run_exp ab_e4_batch2 ab_e4.yaml 60); echo "$R4"
else
  R4="skipped(peak=$peak)"
  say "E4 跳过：显存峰值 $peak >= 13500MB 或不可用"
fi

# ---------- E5 验证跑（150 步）：若 768 明显更快则验证 res768，否则验证对照 ----------
VER_FLAGS=""
s3=$(getv "$R3" steady_s_it); ok3=$(getv "$R3" ok)
if [ "$ok3" = "1" ] && [ -n "$s3" ] && awk -v a="$s3" 'BEGIN{exit !(a+0 < 5.0)}'; then
  VER_FLAGS="--res768"
  say "E5 验证对象：res768（E3 steady=${s3}s/it）"
else
  say "E5 验证对象：对照配置（E3 未达标或失败）"
fi
gen ab_e5.yaml --name ab_e5_verify --steps 150 $VER_FLAGS
R5=$(run_exp ab_e5_verify ab_e5.yaml 150); echo "$R5"

say "=== 汇总 ==="
while IFS= read -r l; do say "SUM $l"; done < "$SUMMARY"
say "AB_SUITE_DONE"

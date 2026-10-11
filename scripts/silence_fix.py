#!/usr/bin/env python3
"""乱话段音频静音工具：把 H3 加戏的碎词区间静音（保留画面与正常台词）。
用法: python3 silence_fix.py <mp4路径> <起1> <止1> [<起2> <止2> ...]
原地处理（先备份为 *_pre_audio.mp4）。
"""
import subprocess
import sys
from pathlib import Path

mp4 = Path(sys.argv[1])
pairs = sys.argv[2:]
assert len(pairs) % 2 == 0 and pairs, "需要成对的静音区间（起 止）"
intervals = [(float(pairs[i]), float(pairs[i + 1])) for i in range(0, len(pairs), 2)]

backup = mp4.with_name(mp4.stem + "_pre_audio.mp4")
if not backup.exists():
    subprocess.run(["cp", str(mp4), str(backup)], check=True)

# 构造 volume 滤镜：各区间静音
exprs = "+".join(f"between(t,{a},{b})" for a, b in intervals)
af = f"volume=enable='{exprs}':volume=0"
tmp = mp4.with_name(mp4.stem + "_tmp.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-af", af,
                "-c:v", "copy", "-c:a", "aac", str(tmp)], check=True)
tmp.replace(mp4)
print(f"OK: {mp4.name} <- 静音 {intervals}", flush=True)

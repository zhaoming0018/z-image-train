#!/usr/bin/env python3
"""DV 短片台词合成（Qwen3-TTS VoiceDesign，两句一次生成保同一音色）。

用法: /home/zhaoyiming/miniconda3/bin/python -u scripts/dv_lines.py <out_dir>
"""
import sys
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

MODEL = "/mnt/d/models/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

model = Qwen3TTSModel.from_pretrained(MODEL, device_map="cuda:0", dtype=torch.bfloat16)
instruct = ("约二十岁年轻女性的日常口语，声音清澈自然偏软，像朋友间轻松打趣，"
            "离麦克风近的生活感，不要播音腔")
texts = ["干嘛拍这么近？", "快点跟上。"]
wavs, sr = model.generate_voice_design(text=texts, instruct=instruct, language="Chinese")
sf.write(f"{OUT}/line1.wav", wavs[0], sr)
sf.write(f"{OUT}/line2.wav", wavs[1], sr)
print(f"saved line1.wav ({len(wavs[0])/sr:.2f}s) / line2.wav ({len(wavs[1])/sr:.2f}s), sr={sr}")

#!/usr/bin/env python3
"""第一章动漫集 · 中文台词合成（qwen3-tts VoiceDesign，两音色：老六 / 黑老头）。"""
import sys
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

MODEL = "/mnt/d/models/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

V_L6 = ("二十岁出头的中国市井小青年绰号六爷，嗓音清晰，带一点痞气、懒散随性，"
        "像在跟朋友吹牛打屁，自嘲口吻，不高不低，日常距离感，不要播音腔")
V_HE = ("七老八十的中国江湖算命老头，嗓音沙哑苍老、慢条斯理、故作神秘，"
        "带一丝狡黠的笑意，有颗粒感的老嗓子")

LINES = [
    # (文件名, 音色, 台词)
    ("s1_narr", V_L6, "我叫刘朕，绰号刘老六，自号六爷。"),
    ("s2_hei",  V_HE, "小朋友，你今天有挂，六爷是吧？"),
    ("s3_l6",   V_L6, "你是饭馆退休的吧？"),
    ("s4_l6",   V_L6, "你敢说我胖？！"),
    ("s5_hei",  V_HE, "掌气起寒霜，六爷有痔疮。"),
]

model = Qwen3TTSModel.from_pretrained(MODEL, device_map="cuda:0", dtype=torch.bfloat16)

# 按音色分组批量合成（同批音色更一致）
from collections import OrderedDict
groups = OrderedDict()
for fn, voice, text in LINES:
    groups.setdefault(voice, []).append((fn, text))

for voice, items in groups.items():
    texts = [t for _, t in items]
    wavs, sr = model.generate_voice_design(text=texts, instruct=voice, language="Chinese")
    for (fn, _), w in zip(items, wavs):
        path = f"{OUT}/{fn}.wav"
        sf.write(path, w, sr)
        print(f"saved {path} ({len(w)/sr:.2f}s)", flush=True)
print("ALL_DONE", flush=True)

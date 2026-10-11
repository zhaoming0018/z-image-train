#!/usr/bin/env python3
"""第二章完整版 · 18 镜 × 15 秒 i2v（MiniMax H3，H3 原生中文台词）。
幂等：已存在自动跳过；单镜重跑 = 删该镜 mp4 后重跑。
产出：WORK/ep2v2_fNN_*.mp4（WORK=/home/zhaoyiming/.hermes/cache/scratch/ep2v2）
"""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = "/home/zhaoyiming/z-image-train"
WORK = Path("/home/zhaoyiming/.hermes/cache/scratch/ep2v2")
WORK.mkdir(parents=True, exist_ok=True)
VIDEO_DIR = Path("/mnt/d/minimax-h3-demo/ComfyUI/output/video")
INPUT_DIR = "/mnt/d/minimax-h3-demo/ComfyUI/input"
SCRATCH = "/home/zhaoyiming/.hermes/cache/scratch"
WF_SRC = "/mnt/d/minimax-h3-demo/workflows/video_minimax_h3_i2v.json"
DUR = 15

ONLY = "the characters speak ONLY the exact quoted Chinese lines, word for word, no improvised extra words; "
TALE = "the flat simple anime background stays unchanged; smooth limited TV-anime animation"

SHOTS = [
    ("f01_street", 601, "anime_ch2full_f01_street.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man in the white tank top walks down the busy small-town lane; his voice-over in Chinese: "
     "「在北台，堡子街绝对算是最繁华的一段闹区——抻面馆旁边开修车厂，KTV 右边是瑜伽馆，"
     "网吧开在幼儿园旁边，最夸张的是北台分局，夹在游艺厅和洗浴中心中间。」; only one young man, no other people; " + TALE),
    ("f02_sign", 602, "anime_ch2_s1_sign.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man stands at the restaurant entrance looking up at the 「北台肥羊」 signboard and mutters "
     "in Chinese: 「啤酒饮料打九折，锅底免费另送菜碟儿——富老大就安排这地方吃饭？」; then he adds: "
     "「嘶……办完事还得回去揍他一顿。」; only one young man, no other people; " + TALE),
    ("f03_hotpot", 603, "anime_ch2full_f03_hotpot.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man pushes the door open and the steam rushes over him; he grimaces and gasps in Chinese: "
     "「这热浪，夹着膻味儿——我一口气儿差点没上来。」; only one young man, no other people; " + TALE),
    ("f04_dismiss", 604, "anime_ch2full_f04_dismiss.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man walks on waving one hand dismissively and mutters in Chinese: "
     "「说起来这家店也有一段历史了……不过去年，老板让我运了一批死耗子肉过来——从那以后，"
     "我跟天下所有的羊肉产品划清了界限。」; only one young man, no other people; " + TALE),
    ("f05_frontdesk", 605, "anime_ch2_s2_frontdesk.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the waitress in the pink uniform greets him sweetly in Chinese: 「六哥来啦~」; the chubby young man snaps: "
     "「叫什么叫！六爷办正事儿呢！」; the waitress rolls her eyes and goes back to cracking sunflower seeds; "
     "exactly two people, no duplicates; " + TALE),
    ("f06_manager", 606, "anime_ch2_s3_manager.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the manager in the dark vest says in Chinese: 「老六来啦？富老大在楼上 203。」; the chubby young man blinks: "
     "「楼上？203？」; the manager leans in with a low voice: 「最近查得严，仓库改了个包房。」; "
     "exactly two people, no duplicates; " + TALE),
    ("f07_stairs", 607, "anime_ch2full_f07_stairs.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man squeezes up the narrow staircase, pushing past stacked tables, and mutters in Chinese: "
     "「华容道似的——搬桌子推椅子，左拐右钻……回想起上回往上面搬死耗子，又是一阵阵反胃。」; "
     "only one young man, no other people; " + TALE),
    ("f08_boss", 608, "anime_ch2full_f08_boss.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man greets at the door in Chinese: 「老大。」; the boss looks up: 「老六来啦。」; then the "
     "boss stares behind him and his face drops: 「你的人呢？又是你自己来？！」; exactly two people, no duplicates; " + TALE),
    ("f09_fawn", 609, "anime_ch2full_f09_fawn.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man bows apologetically and explains in Chinese: 「最近兄弟们都忙，就剩俩手脚利索的还放年假了——"
     "要不是富老大有话，我都抽不开身。」; the boss watches him unimpressed; exactly two people, no duplicates; " + TALE),
    ("f10_slam", 610, "anime_ch2_s4_slam.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the boss slams the table furiously and yells in Chinese: 「去你蛋的！」; then he points with his cigarette: "
     "「你个小崽子是想让我丢人啊？！今天来的全是北台有头有脸的大哥——你要是不帮我把脸撑住喽，"
     "我他妈给你卖矿山上去！！」; the chubby young man shrinks with an apologetic smile; exactly two people, "
     "no duplicates; " + TALE),
    ("f11_light", 619, "anime_ch2full_f11_light.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man bends over to guide the boss's cigarette hand back to his mouth — both men's hands stay "
     "clearly separate with simple clean fingers, no merging or overlapping of hands; saying in "
     "Chinese: 「我错了，我错了，老大你消消气——我这就给你叫人去。说吧，要多少兄弟。」; exactly two people, "
     "no duplicates; " + TALE),
    ("f12_lean", 612, "anime_ch2full_f12_lean.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the boss leans back in his chair with narrowed eyes and says in Chinese: 「哼……今天就是和几个老大随便聊聊——"
     "你就给我找几个像样的就行，别他妈总一个人跑来装犊子！」; the chubby young man stands listening; "
     "exactly two people, no duplicates; " + TALE),
    ("f13_flee", 613, "anime_ch2_s5_flee.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man hurries out through the door bowing; he yelps in Chinese: 「诶~诶~~」; from behind him the "
     "boss's furious voice yells: 「刘老六！！他妈的我烟呢，是不是又让你顺跑了！！！」; only one young man in view; " + TALE),
    ("f14_cigs", 614, "anime_ch2full_f14_cigs.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man walks out onto the street and slips the cigarette pack into his waistband; his voice-over "
     "in Chinese: 「要不说在北台像我这样的其实挺不好混的——没啥大能耐，就能干些坑蒙拐骗的事；拐还不敢拐人，"
     "偷个鸡摸个狗卖俩打牙祭的钱——整天摸爬滚打的，其实也就混了一口饭吃。」; only one young man, no other people; " + TALE),
    ("f15_netbar", 620, "anime_ch2full_f15_netbar.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man squeezes between two rows of chairs in the noisy internet cafe; the voices around shout "
     "in Chinese: 「毒他毒他！！瞎啊，那个是我！！」; then another voice: 「我先飞了，顶不住！」; "
     "only one clear young man; his white tank top stays clean white throughout, no stains; " + TALE),
    ("f16_huiming", 623, "anime_ch2_s6_netbar.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the skinny young man standing on the chair yells angrily in Chinese: 「谁他妈扔的闪光？！瞎啊？！自己人都闪？」— "
     "he yells ONLY this one line, nothing said before or after it, no other words at all; "
     "exactly two people, no duplicates; " + TALE),
    ("f17_kick", 624, "anime_ch2_s6_netbar.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man kicks the chair from below and snaps in Chinese: 「叫毛呢！」; the skinny young man jumps "
     "down with a grin: 「哎呦，六哥！你怎么跑这来了？」; the chubby young man pulls him: 「跟我办点事去，急着呢。」— "
     "ONLY these three lines, no words before or after them, no additional sentences; "
     "exactly two people, no duplicates; " + TALE),
    ("f18_ak", 618, "anime_ch2full_f18_screen.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the skinny young man sits back down at the desk saying in Chinese: 「你等会啊！我这最后一局了。」; the chubby "
     "young man grabs at the mouse; the skinny young man wails: 「完了，爆了爆了！」; a voice from the far row shouts: "
     "「爆什么了？先给我啊！」; the skinny young man rolls his eyes: 「叫个毛叫！爆了把ＡＫ，你要啊？！」; "
     "exactly two people in focus, no duplicates; " + TALE),
]

for tag, seed, img, _ in SHOTS:
    src = f"{ROOT}/output/liulaoliu_story/sheets/{img}"
    if os.path.exists(src):
        shutil.copy(src, f"{INPUT_DIR}/{img}")
print("[prep] input images synced", flush=True)


def snap():
    return set(p.name for p in VIDEO_DIR.glob("*.mp4"))


def run_shot(tag, seed, img, prompt):
    dst = WORK / f"ep2v2_{tag}.mp4"
    if dst.exists():
        print(f"[skip] {tag} (exists)", flush=True)
        return
    base = json.load(open(WF_SRC))
    for n in base["nodes"]:
        if n.get("id") == 114:
            n["widgets_values"][0] = img
        if n.get("id") == 105:
            n["widgets_values"][0] = prompt
            n["widgets_values"][3] = DUR
            n["widgets_values"][4] = seed
        if n.get("id") == 115 and isinstance(n["widgets_values"][0], str) \
                and n["widgets_values"][0].startswith("1:1"):
            n["widgets_values"][0] = "16:9 (Widescreen)"
    wf_path = f"{SCRATCH}/h3_ep2v2_{tag}.json"
    json.dump(base, open(wf_path, "w"), ensure_ascii=False, indent=1)

    before = snap()
    env = dict(os.environ)
    env["NO_PROXY"] = "127.0.0.1,localhost"
    env["COMFY_LOCAL_URL"] = "http://127.0.0.1:8199"
    t0 = time.time()
    r = subprocess.run(
        ["/home/zhaoyiming/.local/bin/comfy", "run", "--workflow", wf_path, "--wait", "--timeout", "3600"],
        env=env, capture_output=True, text=True, timeout=3600)
    out = r.stdout + r.stderr
    if r.returncode != 0 or '"ok": true' not in out:
        raise RuntimeError(f"{tag} comfy run failed: {out[-500:]}")
    new = snap() - before
    if not new:
        raise RuntimeError(f"{tag}: no new video found")
    shutil.copy(VIDEO_DIR / sorted(new)[-1], dst)
    print(f"[{tag}] seed={seed} dur={DUR} {time.time()-t0:.1f}s -> {sorted(new)[-1]}", flush=True)


for tag, seed, img, prompt in SHOTS:
    run_shot(tag, seed, img, prompt)

print("ALL_DONE", flush=True)

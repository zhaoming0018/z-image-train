#!/usr/bin/env python3
"""第三章《出头》· 20 镜 × 15 秒 i2v（MiniMax H3，H3 原生中文台词，seedance 结构 prompt）。
幂等：已存在自动跳过；单镜重跑 = 删该镜 mp4 后重跑。
产出：WORK/ep3_sNN_*.mp4（WORK=scratch/ep3）
"""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = "/home/zhaoyiming/z-image-train"
WORK = Path("/home/zhaoyiming/.hermes/cache/scratch/ep3")
WORK.mkdir(parents=True, exist_ok=True)
VIDEO_DIR = Path("/mnt/d/minimax-h3-demo/ComfyUI/output/video")
INPUT_DIR = "/mnt/d/minimax-h3-demo/ComfyUI/input"
SHEETS = f"{ROOT}/output/liulaoliu_story/sheets"
SCRATCH = "/home/zhaoyiming/.hermes/cache/scratch"
WF_SRC = "/mnt/d/minimax-h3-demo/workflows/video_minimax_h3_i2v.json"
DUR = 15

ONLY = "the characters speak ONLY the exact quoted Chinese lines, word for word, no improvised extra words; "
TALE = "flat simple anime background stays unchanged; smooth limited TV-anime animation"

SHOTS = [
    ("s01_netbar_out", 801, "anime_ch3src_s01_netbar_out.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "outside the internet cafe in bright sunlight: the skinny young man squints hard and shields his eyes, groaning "
     "in Chinese: 「什么事这么急啊？」; the chubby young man answers: 「富老大那边找人撑场面——要像点样的，我这不就想起"
     "你来了嘛。」; exactly two people, no duplicates; " + TALE),
    ("s02_walk", 802, "anime_ch3src_s02_walk.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man pulls the skinny young man along the street, walking fast; brief talk in Chinese: "
     "「今天场面大，你收拾收拾，别给六爷丢人。」; 「行行行，别拽别拽。」; exactly two people, no duplicates; " + TALE),
    ("s03_huiming", 803, "anime_ch3src_s03_huiming.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "medium portrait of the skinny young man smoothing down his old suit, his voice-over in Chinese: "
     "「白净的小脸一脑袋卷毛——要不张嘴，别人还以为我是韩国整了容的明星呢。」; only one person in the whole scene; " + TALE),
    ("s04_manager", 804, "anime_ch3src_s04_manager.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "at the restaurant doorway the chubby young man grabs the fleeing manager by the arm, crashing sounds from "
     "inside; he demands in Chinese: 「怎么了这是？！」; the manager wails: 「快叫警察吧，老富在里面让人给砍啦！！！」; "
     "exactly two people, no duplicates; " + TALE),
    ("s05_grit", 805, "anime_ch3src_s05_grit.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "close-up of the chubby young man clenching his jaw in fury, low angle: he takes a breath and speaks in "
     "Chinese: 「兄弟，出头的机会终于来了——能不能闯出个名堂，就看今天！」; only one person in the whole scene; " + TALE),
    ("s06_stairs", 876, "anime_ch3src_s06_stairs.png",
     "anime style 2D animation, cel-shaded: the chubby young man charges up the old staircase, taking the steps "
     "two at a time, dust kicking up; absolutely no speech, no voices, no talking at all — only heavy footsteps "
     "and faint muffled thuds from above; only one person in the whole scene; " + TALE),
    ("s07_room", 857, "anime_ch3src_s07_room.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the wrecked private room in a wide shot: the bleeding boss defiantly at the round table, the bald fat man "
     "with the watermelon knife leering; quiet tense room tone only, no action, no fighting; nobody ever enters "
     "or moves through the frame, the camera stays on these two the whole time; the bald man sneers in Chinese: "
     "「老富，你还真不给面子啊？」; exactly two people, never anyone else; " + TALE),
    ("s08_youtou", 808, "anime_ch3src_s08_youtou.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the bald fat boss glares and raps the table with the flat of his knife, snarling in Chinese: 「你嫂子敬你酒你"
     "不喝，亲手赏你的菜你也不吃？」; only one clear person; " + TALE),
    ("s09_laofu", 809, "anime_ch3src_s09_laofu.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the bloody boss sits bolt upright, pointing fiercely, roaring in Chinese: 「我糖尿病你也不是不知道！油头，"
     "你今天不就是想灭我威风吗——有种就让我富强以后站不起来，不然我非拆了你这间破庙！！」; "
     "only one clear person; " + TALE),
    ("s10_bottle", 890, "anime_ch3src_s10_bottle.png",
     "anime style 2D animation, cel-shaded: THE single most important moment — the green beer bottle BREAKS "
     "APART on the boss's head: the bottle snaps in two, the top half flies away and countless green glass shards "
     "spray through the air like fireworks; the boss's jowly face with the pencil mustache stays clearly visible, "
     "slumping forward; no dialogue, only the crash of breaking glass; exactly two people; " + TALE),
    ("s11_shout", 861, "anime_ch3src_s11_shout.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man KICKS the door open and bursts through it brandishing a green bottle high, bellowing in "
     "Chinese: 「都他妈给我住手！！！」; door slamming open, dramatic low angle; only one person in the whole scene; "
     + TALE),
    ("s12_feige", 812, "anime_ch3src_s12_feige.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the lean thug in the black leather jacket leaps onto the tabletop and sneers down in Chinese: 「他娘的刘老六，"
     "你找死呢？！」; cold arrogant face, low angle making him loom; only one clear person; " + TALE),
    ("s13_slap", 813, "anime_ch3src_s13_slap.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the lean thug slaps the chubby young man across the face again and again, snarling in Chinese: 「怎么着？就你"
     "还想出头啊？！」; the young man's head rocks with each slap, dazed; exactly two people, no duplicates; " + TALE),
    ("s14_kick", 814, "anime_ch3src_s14_kick.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the skinny young man in the shabby suit lunges from behind and kicks the lean thug hard in the stomach with a "
     "cry: 「我草！！」; the thug doubles over with a scream; dynamic action; exactly two people, no duplicates; " + TALE),
    ("s15_laofu2", 865, "anime_ch3src_s15_laofu2.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the bloody boss, propped on the table, suddenly yells at the chubby young man in Chinese: 「看毛呢！！！你最"
     "拿手的不就是打老头儿嘛？！」; he points at the surrounding old guests — ALL of the guests are completely "
     "dark faceless blurry silhouettes, no facial features, never detailed, no plates or food appear; " + TALE),
    ("s16_melee", 866, "anime_ch3src_s16_melee.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the brawl in one single continuous action: the chubby young man smashes his green bottle on the thug's head, "
     "then ducks and lands an uppercut on the bald fat man knocking him down; heavy impact sounds and shouting; "
     "the same restaurant background stays unchanged the whole time; exactly two people visible at a time; " + TALE),
    ("s17_fist", 867, "anime_ch3test_fist.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the young man smashes his fist straight down onto the incoming watermelon knife — the bent blade FLIES OUT "
     "of the bald man's hand, spinning away; the bald boss freezes in wide-eyed shock, jaw dropped; then the young "
     "man looks stunned at his own fist; camera shake at the impact; no dialogue, metal clang and gasps only; "
     "exactly two people, no duplicates; " + TALE),
    ("s18_wall", 878, "anime_ch3src_s18_wall.png",
     "anime style 2D animation, cel-shaded: BOOM — the young man's left fist smashes clean through the wall: a "
     "huge hole bursts open, brick rubble explodes, white steam from the bathhouse next door billows in; everyone "
     "else already fled; absolutely no speech, no voices at all — only the massive impact boom, rubble clatter "
     "and steam hiss; only one clear person; " + TALE),
    ("s19_hand", 819, "anime_ch3src_s19_hand.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the chubby young man stares at his own left fist, wide-eyed, then hurries to shove it into his trouser "
     "pocket, muttering in Chinese: 「没事……没事……」; only one person in the whole scene; " + TALE),
    ("s20_phone", 820, "anime_ch3src_s20_phone.png",
     "anime style 2D animation, cel-shaded: " + ONLY +
     "the bloodied boss props himself up and roars at the young man in Chinese: 「还愣着干什么？看着我死啊！！！」; "
     "the young man panics and shouts: 「快打114——厄不对——快打119——急救电话是多少来着！！快打112去问！！！」; "
     "exactly two people, no duplicates; " + TALE),
]

# 源图同步到 input
for _, _, img, _ in SHOTS:
    src = f"{SHEETS}/{img}"
    if os.path.exists(src):
        shutil.copy(src, f"{INPUT_DIR}/{img}")
print("[prep] input images synced", flush=True)


def snap():
    return set(p.name for p in VIDEO_DIR.glob("*.mp4"))


def run_shot(tag, seed, img, prompt):
    dst = WORK / f"ep3_{tag}.mp4"
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
    wf_path = f"{SCRATCH}/h3_ep3_{tag}.json"
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

#!/usr/bin/env python3
"""第一章完整版（16 镜 × 15 秒）· H3 i2v，台词原生中文。
幂等：已存在自动跳过；单镜重跑 = 删该镜 mp4 后重跑。
产出：WORK/ep1v2_eNN_*.mp4（WORK=/home/zhaoyiming/.hermes/cache/scratch/ep1v2）
"""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = "/home/zhaoyiming/z-image-train"
WORK = Path("/home/zhaoyiming/.hermes/cache/scratch/ep1v2")
WORK.mkdir(parents=True, exist_ok=True)
VIDEO_DIR = Path("/mnt/d/minimax-h3-demo/ComfyUI/output/video")
INPUT_DIR = "/mnt/d/minimax-h3-demo/ComfyUI/input"
SCRATCH = "/home/zhaoyiming/.hermes/cache/scratch"
WF_SRC = "/mnt/d/minimax-h3-demo/workflows/video_minimax_h3_i2v.json"
DUR = 15  # 15 秒档（duration 为自由浮点）

SHOTS = [
    ("e01_intro", 501, "anime_ch1_s1_strut_clean.png",
     "anime style 2D animation, cel-shaded: a single person in the scene, only one young man, no one else — "
     "the chubby young man in the white tank top struts toward the camera with a cocky swagger, and says in "
     "Chinese: 「我叫刘朕，绰号刘老六，自号六爷。」; then he grins: 「可为什么大家都喜欢叫我败类？」; "
     "then he shrugs and continues: 「就因为我平日里游手好闲，没有一技之长，还打过几个老头儿？」; "
     "the flat simple anime street background stays unchanged; smooth limited TV-anime animation"),
    ("e02_curb", 502, "anime_ch1full_n1_crouch.png",
     "anime style 2D animation, cel-shaded: the chubby young man squats on the curb smoking, exhales a puff of "
     "smoke with a cynical look, and mutters in Chinese: 「我承认我没什么上进心。」; then he smirks: "
     "「不过凭着交际能力，和废品站的富老大也攀上了点关系——打打零工，帮人撑撑场面，买盒烟就得省顿饭，"
     "饿不死。」; only one young man, no other people; the flat simple anime background stays unchanged; "
     "smooth limited TV-anime animation"),
    ("e03_excited", 503, "anime_ch1full_n2_excited.png",
     "anime style 2D animation, cel-shaded: the chubby young man raises both fists to the sky and says excitedly "
     "in Chinese: 「今天接了个大活！富老大晚上请几个老板吃饭，叫我带人站台，200块！」; then his eyes sparkle: "
     "「这不光是买卖，是出头上位的机会！刘老六，你啥时候成为北台第一？就在今天！！！」; "
     "only one young man, no other people; the flat simple anime background stays unchanged; smooth limited "
     "TV-anime animation"),
    ("e04_block", 527, "anime_ch1_s2_block.png",
     "anime style 2D animation, cel-shaded: the elderly fortune-teller raises his dark hand to block the way; "
     "the chubby young man snaps in Chinese: 「干什么？」; the old man cackles: 「小朋友，你今天有挂，恩……六爷是吧？」; "
     "the young man replies smugly: 「什么六爷，江湖上的朋友给面子。」; after that, the old man retracts his hand and "
     "rubs both hands together with a grin, tiny dark mud crumbs flaking off his dirty fingers and falling down; "
     "the young man grimaces in disgust; exactly two people, no duplicates; "
     "the flat simple anime street background stays unchanged; smooth limited TV-anime animation"),
    ("e05_booth", 505, "anime_ch1full_n3_booth.png",
     "anime style 2D animation, cel-shaded: the chubby young man walks up to the shabby fortune-teller booth and "
     "looks down at the cloth on the ground, and says skeptically in Chinese: 「这就是你的摊儿？连桌子都没有。」; "
     "then he points at the drawings: 「这八卦画得跟烧饼似的……这手，鸡爪子是吧？」; the old fortune-teller "
     "grins without a word; exactly two people, no duplicates; the flat simple anime background stays unchanged; "
     "smooth limited TV-anime animation"),
    ("e06_shake", 506, "anime_ch1_s3_shake.png",
     "anime style 2D animation, cel-shaded: the chubby young man sits on the small stool shaking the bamboo "
     "fortune-stick tube and asks in Chinese: 「你是饭馆退休的吧？」; the old fortune-teller narrows his eyes at "
     "him and answers: 「六爷的面相好啊，天庭饱满……」; exactly two people, no duplicates; the flat simple anime "
     "background stays unchanged; smooth limited TV-anime animation"),
    ("e07_fat", 521, "anime_ch1_s4_palm.png",
     "anime style 2D animation, cel-shaded: the characters speak ONLY the exact quoted Chinese lines, word for "
     "word, no improvised extra words; the chubby young man raises one palm out frowning and snaps in "
     "Chinese: 「你敢说我胖？！」; the old man waves his hands: 「没有，没有那个意思。」; "
     "exactly two people, no duplicates; the flat simple anime background stays unchanged; smooth limited "
     "TV-anime animation"),
    ("e08_probe", 508, "anime_ch1full_n4_probe.png",
     "anime style 2D animation, cel-shaded: the elderly fortune-teller leans forward rubbing his dirty hands "
     "together with a sly grin, and probes in Chinese: 「吭~那个……听说六爷擅打老头儿？！」; "
     "only one old man in the scene; the flat simple anime background stays unchanged; smooth limited "
     "TV-anime animation"),
    ("e09_smash", 528, "anime_ch1full_n5_smash.png",
     "anime style 2D animation, cel-shaded: the young man does not laugh, does not giggle, no laughing sounds; "
     "he speaks ONLY the exact quoted Chinese line, word for word, no extra words, no other language; "
     "the chubby young man suddenly explodes — he flings the bamboo "
     "fortune-stick tube down to the ground with sticks scattering, shouting in Chinese: 「你耍我玩呐？！」; "
     "only one young man, no other people; the flat simple anime street background stays unchanged; smooth "
     "limited TV-anime animation"),
    ("e10_grip", 510, "anime_ch1full_n6_grip.png",
     "anime style 2D animation, cel-shaded: the elderly fortune-teller grips the young man's wrist like an iron "
     "clamp and says calmly in Chinese: 「不可动怒啊~」; the chubby young man pulls back desperately shouting: "
     "「松开！！你特么给我松开！！」; exactly two people, no duplicates; the flat simple anime background stays "
     "unchanged; smooth limited TV-anime animation"),
    ("e11_palm", 529, "anime_ch1full_n7_palm.png",
     "anime style 2D animation, cel-shaded: the elderly fortune-teller holds the young man's open palm firmly and draws "
     "lines ON THE YOUNG MAN'S PALM with one dirty finger — the drawing happens on the young man's hand, never on his own hand — chanting mysteriously in Chinese: 「掌中多筋包，不抓鞭子就抓刀…"
     "命理有黑痣，逆天违伦方得势……」; the young man stares at him, unease growing; exactly two people, "
     "no duplicates; the flat simple anime background stays unchanged; smooth limited TV-anime animation"),
    ("e12_virgin", 523, "anime_ch1full_n8_flushed.png",
     "anime style 2D animation, cel-shaded: the characters speak ONLY the exact quoted Chinese lines, word for "
     "word, no improvised extra words; the old fortune-teller's voice continues in Chinese: "
     "「精气聚成团，六爷原来是处男……」; the chubby young man's face breaks into a layer of cold sweat, "
     "eyes wide in disbelief; only one face on screen; the flat simple anime background stays unchanged; "
     "smooth limited TV-anime animation"),
    ("e13_wetbed", 532, "anime_ch1full_n8_flushed.png",
     "anime style 2D animation, cel-shaded: a tight portrait close-up of the chubby young man's sweaty face from "
     "start to end — absolutely no other character of any kind appears on screen, no old man, no taoist, no monk, "
     "only the young man's face; the old fortune-teller's voice is heard off-screen in Chinese: "
     "「童子线挺长，十八左右还尿床……」; the chubby young man snaps, sweating, shouting: 「你给我松开听到没？！」; "
     "only one face on screen; the flat simple anime background stays unchanged; smooth limited TV-anime animation"),
    ("e14_piles", 531, "anime_ch1full_e14_empty.png",
     "anime style 2D animation, cel-shaded: the characters speak ONLY the exact quoted Chinese lines, word for "
     "word, no improvised extra words; the young man stands EMPTY-HANDED, fists clenched at his sides, nothing in "
     "his hands; the old fortune-teller chants with fingers pinched in Chinese: "
     "「掌气起寒霜，六爷有痔疮，掌峰似坚壁，你大便很吃力啊。」; the chubby young man freezes, face contorted "
     "with rage; exactly two people, no duplicates; the flat simple anime background stays unchanged; "
     "smooth limited TV-anime animation"),
    ("e15_stool", 517, "anime_ch1_s5_stool.png",
     "anime style 2D animation, cel-shaded: BANG!!! — the chubby young man swings the small wooden stool down on "
     "the old man's head furiously, the stool shatters; then he shouts in Chinese: 「你是老天爷派下来玩我的吧？！"
     "」; the old man flinches on the ground with hands over his face; exactly two people, no duplicates; "
     "the flat simple anime background stays unchanged; smooth limited TV-anime animation"),
    ("e16_crowd", 516, "anime_ch1_s6_after.png",
     "anime style 2D animation, cel-shaded: the chubby young man stands panting with the broken wooden stool in "
     "one hand; the old fortune-teller lies crumpled on the ground; blurred bystanders gather and a voice shouts "
     "in Chinese: 「大家都来看诶！刘老六又打老头儿了！！！」; the flat simple anime background stays unchanged; "
     "smooth limited TV-anime animation"),
]

for tag, seed, img, _ in SHOTS:
    src = f"{ROOT}/output/liulaoliu_story/sheets/{img}"
    if os.path.exists(src):
        shutil.copy(src, f"{INPUT_DIR}/{img}")
print("[prep] input images synced", flush=True)


def snap():
    return set(p.name for p in VIDEO_DIR.glob("*.mp4"))


def run_shot(tag, seed, img, prompt):
    dst = WORK / f"ep1v2_{tag}.mp4"
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
    wf_path = f"{SCRATCH}/h3_ep1v2_{tag}.json"
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

#!/usr/bin/env python3
"""第三章《出头》分镜图批量：18 张新图（Qwen 参考图锁人）。
产出：output/liulaoliu_story/sheets/anime_ch3src_s*.png；已存在自动跳过。
"""
import json
import os
import shutil
import time
import urllib.request
from pathlib import Path

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)

ROOT = "/home/zhaoyiming/z-image-train"
BRIDGE = "http://127.0.0.1:8199"
COMFY_OUT = "/mnt/d/minimax-h3-demo/ComfyUI/output"
DEST = Path(f"{ROOT}/output/liulaoliu_story/sheets")
INPUT = "/mnt/d/minimax-h3-demo/ComfyUI/input"

STYLE = ("Japanese anime style illustration, a still frame from a TV anime, cel shading, clean line art, "
         "simple flat anime background: ")
TAIL = ("; everything simple, clean and flat, clearly a hand-drawn anime scene, not realistic, no photo texture; "
        "warm pastel anime color design")
NEG = ("photorealistic, photo, 3d render, gradient shading, grunge, painterly, detailed background, "
       "extra people, duplicate person")

# (name, seed, [ref cards], body)
SHOTS = [
    ("s01_netbar_out", 171, ["card_l6liu_anime.png", "card_huiming_anime.png"],
     "outside an old internet cafe in bright morning sunlight: the skinny young man in the shabby oversized suit "
     "from the SECOND reference image staggers out squinting hard against the sun, one hand raised to shield his "
     "eyes, looking exhausted after an all-nighter; the chubby young man from the FIRST reference image stands "
     "next to him; exactly two people in the whole scene, no duplicates"),
    ("s02_walk", 191, ["card_l6liu_anime.png", "card_huiming_anime.png"],
     "two young men hurry down an old small-town street — clearly ON the street, with shuttered shops and signs on "
     "both sides behind them: the chubby young man from the FIRST reference image walks briskly pulling the skinny "
     "shabby-suit young man from the SECOND reference image along by the arm, both walking with urgency; "
     "exactly two people in the whole scene, no duplicates"),
    ("s03_huiming", 173, ["card_huiming_anime.png"],
     "medium close-up portrait of the skinny young man in the old oversized dark suit from the reference image: "
     "fair handsome face, natural curly black hair, drowsy cynical expression; simple flat anime street background "
     "blurred behind; only one person in the whole scene"),
    ("s04_manager", 200, ["card_l6liu_anime.png"],
     "at the doorway of an old restaurant with faint crashing sounds from inside: the chubby young man from the "
     "reference image grabs by the arm a panicked middle-aged restaurant manager in a dark vest who is cowering "
     "while running out; the manager has a startled face; a full single scene showing ONLY these two men at the "
     "doorway — nothing else in frame, no floating head, no face in the corner, no other figures, no duplicates"),
    ("s05_grit", 175, ["card_l6liu_anime.png"],
     "close-up of the chubby young man from the reference image clenching his jaw with fierce determined eyes, "
     "sweat on his forehead, standing before a doorway; dramatic low angle; simple flat anime background; "
     "only one person in the whole scene"),
    ("s06_stairs", 176, ["card_l6liu_anime.png"],
     "the chubby young man from the reference image charges up an old restaurant staircase two steps at a time, "
     "body leaning forward, motion lines, the door upstairs hanging half off its hinges; dynamic action angle; "
     "only one person in the whole scene"),
    ("s07_room", 201, ["card_fu6lao_anime.png", "card_youtou_anime.png"],
     "inside a wrecked restaurant private room: the stocky middle-aged boss from the FIRST reference image sits "
     "defiantly at the round table with a bloody forehead; the bald fat boss from the SECOND reference image — "
     "looking EXACTLY like that reference: bare shiny bald head, thick stubble, huge belly, ragged white undershirt, "
     "NO hat, NO headwear — stands menacingly to the side holding a big watermelon knife; ONLY these two men in the "
     "room, no third figure; simple flat anime interior"),
    ("s08_youtou", 178, ["card_youtou_anime.png"],
     "close-up of the bald fat boss from the reference image, glaring ferociously, holding a large Chinese "
     "watermelon knife, a vicious grin, flies buzzing around his oily bald head; low angle; simple flat anime "
     "interior background; only one person in the whole scene"),
    ("s09_laofu", 194, ["card_fu6lao_anime.png"],
     "the stocky middle-aged boss from the reference image sits bleeding from the forehead at the table, jaw "
     "clenched, eyes blazing with defiant rage, pointing with a trembling finger; only ONE man in the whole scene, "
     "alone at the table, no other people at all; simple flat anime restaurant interior"),
    ("s10_bottle", 195, ["card_fu6lao_anime.png"],
     "violent moment in a wrecked restaurant private room: a dark blurry thug silhouette swings a green beer bottle "
     "down onto the head of the stocky boss from the reference image seated at the table — the boss's jowly face "
     "with the pencil mustache is clearly visible and recognizable, his head snapping down, broken glass flying; "
     "dynamic impact composition, motion lines; exactly two people in the scene"),
    ("s11_shout", 181, ["card_l6liu_anime.png"],
     "the chubby young man from the reference image bursts through the doorway of a wrecked private room, "
     "brandishing a green beer bottle, shouting furiously with fierce eyes; dramatic low angle, action entrance; "
     "simple flat anime interior; only one person in the whole scene"),
    ("s12_feige", 182, ["card_ningfei_anime.png"],
     "the lean wiry street thug in a black leather jacket from the reference image leaps onto a round tabletop and "
     "crouches there glaring down with cold arrogance, one hand slapping; seen from low angle making him loom; "
     "simple flat anime restaurant interior; only one person in the whole scene"),
    ("s13_slap", 183, ["card_l6liu_anime.png", "card_ningfei_anime.png"],
     "the lean wiry thug from the SECOND reference image slaps the chubby young man from the FIRST reference image "
     "across the face; the young man's head rocks sideways, cheek turning red, dazed expression; dynamic slap "
     "motion lines; exactly two people, no duplicates"),
    ("s14_kick", 196, ["card_huiming_anime.png", "card_ningfei_anime.png"],
     "the skinny young man in the shabby oversized suit from the FIRST reference image (NO leather jacket — baggy "
     "frayed dark suit) lunges and kicks the wiry thug in the black leather jacket from the SECOND reference image "
     "hard in the stomach; the thug doubles over mid-cry, kicking leg extended with motion lines; the two men look "
     "clearly different — one baggy-suited and slim, one leather-jacketed with shaved sides; dynamic action shot; "
     "exactly two people, no duplicates"),
    ("s15_laofu2", 197, ["card_fu6lao_anime.png"],
     "the stocky boss from the reference image, bleeding and disheveled at the table, roars and points at the "
     "cluster of old gangster guests around the room; his finger jabs fiercely; ONLY the boss is a clear person — "
     "everyone else in the room is a simple dark blurry blob silhouette with no facial features; "
     "one clear person in the scene"),
    ("s16_melee", 186, ["card_l6liu_anime.png", "card_ningfei_anime.png"],
     "chaotic brawl inside the wrecked private room: the chubby young man from the FIRST reference image smashes "
     "down on the lean thug from the SECOND reference image who is crouched on the floor, bottles breaking, tables "
     "shoved aside; furious action, motion lines everywhere; exactly two clear people, no duplicates"),
    ("s18_wall", 202, ["card_l6liu_anime.png"],
     "shockwave moment: the chubby young man from the reference image stands with his left fist buried in a huge "
     "fresh hole smashed through the restaurant wall, brick rubble exploding outward, white steam billowing in "
     "through the broken wall, everyone else already gone; dramatic back view, dust and debris, his full body "
     "visible with both legs and both feet clearly drawn standing on the floor; only ONE person in the whole scene "
     "— just this one young man, no duplicate of him anywhere"),
    ("s19_hand", 199, ["card_l6liu_anime.png"],
     "the chubby young man from the reference image, in his white tank top and BLACK SHORTS, stares down at his own "
     "left fist raised in front of him with wide shocked eyes, his other hand about to shove the fist into his "
     "trouser pocket; the focused composition centers on his face and the clenched fist; simple flat anime "
     "background; only one person in the whole scene"),
    ("s20_phone", 189, ["card_fu6lao_anime.png", "card_l6liu_anime.png"],
     "the chubby young man from the SECOND reference image stands in a panic gesturing wildly as if yelling for "
     "someone to call an ambulance; the stocky boss from the FIRST reference image, bloodied, feebly props himself "
     "up on his elbows on the floor shouting at him; comedy emergency scene; exactly two people, no duplicates"),
]

needed = set()
for _, _, refs, _ in SHOTS:
    needed.update(refs)
# 确保所有卡都已在 input
for r in sorted(needed):
    src = DEST / r
    if src.exists():
        shutil.copy(src, f"{INPUT}/{r}")
print("[prep] cards synced:", sorted(needed), flush=True)


def submit(wf):
    req = urllib.request.Request(BRIDGE + "/prompt", data=json.dumps({"prompt": wf}).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))["prompt_id"]


def wait_done(pid, timeout=3600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        with urllib.request.urlopen(f"{BRIDGE}/history/{pid}", timeout=30) as r:
            h = json.load(r)
        if pid in h:
            return h[pid]
        time.sleep(3)
    raise TimeoutError(pid)


tpl = json.load(open(f"{ROOT}/config/qwen21_ref_api.json"))
for name, seed, refs, body in SHOTS:
    out = DEST / f"anime_ch3src_{name}.png"
    if out.exists():
        print(f"[skip] {name} (exists)", flush=True)
        continue
    wf = json.loads(json.dumps(tpl))
    wf["10"]["inputs"]["image"] = refs[0]
    if len(refs) > 1:
        wf["11"] = {"class_type": "LoadImage", "inputs": {"image": refs[1]}}
        wf["4"]["inputs"]["images.image_2"] = ["11", 0]
    wf["4"]["inputs"]["prompt"] = STYLE + body + TAIL
    wf["4"]["inputs"]["negative_prompt"] = NEG
    wf["6"]["inputs"]["seed"] = seed
    wf["5"]["inputs"]["width"] = 1536
    wf["5"]["inputs"]["height"] = 1024
    wf["9"]["inputs"]["filename_prefix"] = f"anime_ch3src_{name}"
    t0 = time.time()
    pid = submit(wf)
    res = wait_done(pid)
    got = False
    for node_out in res.get("outputs", {}).values():
        for img in node_out.get("images", []):
            src = os.path.join(COMFY_OUT, img.get("subfolder", ""), img["filename"])
            if src.lower().endswith((".png", ".jpg", ".webp")):
                shutil.copy(src, out)
                print(f"[still] {name} {time.time()-t0:.1f}s -> {out.name}", flush=True)
                got = True
    if not got:
        print(f"[FAIL] {name}", flush=True)
print("ALL_DONE", flush=True)

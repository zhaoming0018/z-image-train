# 《刘老六传奇》角色库（characters.md）

> 更新：2026-09-30 05:58（v2.8：侯少麟/佟御辉训成——**6/6 全齐**；ch9~10 已交付） ｜ LoRA 目录：ComfyUI `models/loras/`（源：`~/z-image-train/output/<角色>_zimage_lora_v1/`）  ｜ 已训成：l6liu / he6tou / fu6lao / huiming / houshaolin / tongyuhui
> 出图 prompt 规则：**角色块（LoRA 名 + 全描述）＋ 场景动作 ＋ house style**；未训角色用**独立充分文字块**（防同脸）。  
> 定妆候选存档：`output/liulaoliu_story/audition/<slug>/`（生成脚本 `scripts/gen_audition.py`）

## ✅ 已训 LoRA（出图必用 @0.9）

### 刘老六
- **LoRA**：`l6liu_zimage_lora_v1.safetensors` @0.9
- **描述块（逐字复用）**：
  `l6liu, a chubby 23-year-old Chinese street punk with a round face, short messy black hair, small squinting triangular eyes, puffy cheeks, wearing a plain white ribbed tank top, dark knee-length shorts and black flip-flops, a cigarette in his mouth, small pot belly`

### 黑老头 = 老李头儿 = 李景珉（同一人，用户确认）
- **LoRA**：`he6tou_zimage_lora_v1.safetensors` @0.9
- **描述块（扩展自训练 caption，保持语义一致）**：
  `he6tou, an elderly dark-skinned Chinese fortune-teller, grey-white messy hair, deep wrinkles, shabby grey-brown old jacket, beaded bracelet`
- 备注：第一章算命戏出场；第 7 章起以「老李头儿」身份成为主力角色（he6tou LoRA 直接覆盖）

## 🟢 首批：富老大 ✅ · 慧铭 ✅（均已训成）

### 富老大（首批 #1 · slug `fu6lao`）
- **别名**：大名「富强」（大顶子富强 → 富强集团）；部分文本或写作「付老大」——注意原文混写
- **身份**：收废品/收购站起家 → 北台肥羊饭店、富强集团老板
- **外观（原文）**：四十多岁，一米七多的个头，**两撇小胡子**，一脸横肉（像《食神》里做乾坤烧鹅的厨子）；**套过滤嘴的香烟**（标志道具）
- **English 块 v1（定版）**：
  `fu6lao, a stocky Chinese man in his forties, about 1.7m tall, heavy fleshy brutal face with jowls, two thin pencil mustache strips, dark short-sleeved shirt, smoking a cigarette held in a filter holder`
- **定妆**：✅ 用户通过（09-29）；候选 16+2 补拍；淘汰 fu04/07/08/10/11/18（弱脸/手崩/漂移）；主脸锚点 03/06/12/14
- **数据集**：**13 张**（`datasets/fu6lao/`，ds_fu6lao_01~13 + caption）｜一览：`audition/sheet_ds_fu6lao_v2.png`
- **状态**：✅ **训练完成**（09-29 16:21，2500/2500，4.05 s/it，末 loss 0.42）→ `fu6lao_zimage_lora_v1.safetensors` 已拷 ComfyUI；验收：完整角色块成色合格（⚠️ 弱提示会年轻化漂移，出图必带完整块）；**ch3~7 实拍投产 ✅**（多 LoRA 链）
- **受影响旧镜头**：ch2 `s2_boss`/`s3_flatter`（09-29 18:15 已评，详见 PROGRESS「待标记」）

### 刘慧铭（= 晓玄，共肉身；首批 #2 · slug `huiming`）
- **别名**：晓玄（四界特使身份）——**同一肉身，同一 LoRA**
- **外观（原文）**：**白净的小脸、一脑袋的卷毛**（自然卷；「像韩国整了容的明星」的俊俏小白脸）；旧西装（颓废感）；**高度近视**（网吧把脸贴显示器）；全书**未明写戴眼镜**
- **English 块 v2（定版 = 无镜 B 版）**：
  `huiming, a skinny young Chinese man, fair delicate pretty-boy face, natural curly black hair, wearing an old oversized dark suit, shabby faded style`
- **定妆**：✅ 用户拍板：**默认无眼镜**（B 版定版）；**强调「高度近视」的场景才用眼镜版**（A 套 `audition/huiming/` 保留作剧情参考，出图时加 `thick-lensed glasses`）；淘汰 hb19（脸崩）
- **数据集**：**14 张**（`datasets/huiming/`，ds_huiming_01~14 + caption）｜一览：`audition/sheet_ds_huiming_v2.png`
- **状态**：✅ **训练完成**（09-29 19:24，2500/2500，2h49m，4.05 s/it，末 loss 0.366）→ 已拷 ComfyUI；验收：**全块冒烟 ×2 合格**（卷发/无镜/旧西装命中；卷发偏湿感）；**ch3~7 实拍投产 ✅**（多 LoRA 链）
- **受影响旧镜头**：ch2 `s5_cafe`/`s6_drag`（09-29 19:40 已评：均**建议重拍**，详见 PROGRESS「待标记」）

### 侯少麟（首批 #3a · 哼哈二将之一）· ✅ 已训成
- **昵称**：**左青龙**（第 13 章明写）；与佟御辉合称「胖瘦头陀」（**侯=瘦头陀**）
- **外观（第 5~11 章）**：20 岁，**身高 1.93 米大个子**，**谢顶**（低发际线+头顶稀疏、两侧短发），瘦削长身；追 NBA、张口闭口嘻哈「趟子」；纹身「左青龙」（个别镜头加 `a 「左青龙」 tattoo on his forearm`）
- **English 块（定版 · 09-29 拍板；以 `config/illustration.yaml` 为准）**：
  `houshaolin, a very tall lean 20-year-old Chinese young man, 1.93 meters tall, skinny lanky build, early balding with a receding hairline and thinning crown, messy short black hair on the sides, youthful cheeky face, hip-hop street fashion, oversized tee and loose pants, white sneakers`
- **定妆**：✅ 用户通过（09-29 夜）；候选 16；主锚 01/03/11（11 最标准）；弃 14（金发跑偏）/08/09（偏老相）
- **数据集**：**13 张**（`datasets/houshaolin/`）｜训练配置 `config/train/houshaolin_zimage.yaml`
- **状态**：✅ **训练完成**（09-30 02:37；2500/2500，2h51m，4.12 s/it，末 loss 0.378）→ 已拷 ComfyUI；**全块冒烟 ×2 合格**（高瘦/谢顶/街头风命中，含谢顶强化重拍版）；**ch11 起投产**
- 备注：第 11 章「七巧板多色头发」为一次性桥段 → **不入 LoRA**，需要时在 prompt 内加彩发描述

### 佟御辉（首批 #3b · 哼哈二将之一）· ✅ 已训成
- **昵称**：**右白虎**（**佟=胖头陀**）；北台老一辈都叫他「**二子**」
- **外观（第 11~13 章）**：19 岁，**敦实小个子**、圆脸憨厚；发色定版 = **灰白灰白（稳定态）**；**磕巴**（「厄厄厄」「嗷嗷嗷」）、憨傻、**力气大**；纹身「右白虎」（个别镜头加 `a 「右白虎」 tattoo on his forearm`）
- **English 块（定版 · 09-29 拍板；以 `config/illustration.yaml` 为准）**：
  `tongyuhui, a short stocky 19-year-old Chinese youth, round simple good-natured face, messy short hair dyed murky grey-white, plain ill-fitting dark jacket and trousers, sneakers`
- **定妆**：✅ 用户通过（09-29 夜）；候选 16；主锚 11（最标准）/03/16；弃 12（手部融合）
- **数据集**：**14 张**（`datasets/tongyuhui/`）｜训练配置 `config/train/tongyuhui_zimage.yaml`
- **状态**：✅ **训练完成**（09-30 05:38；2500/2500，2h48m，4.05 s/it，末 loss 0.382）→ 已拷 ComfyUI；**全块冒烟 ×2 合格**（矮壮/圆脸/灰白染发命中，含矮壮强化重拍版）；**ch11 起投产**

> ⚠️ **搭档纪律**：侯少麟 + 佟御辉是六爷最早的俩「直系小弟」，几乎总同框 → **同批定妆/训练**（已执行）；同框戏双 LoRA 出场，盯防互相外溢（必要时降强度 / 前后景分离）。

## ⚪ 二批候选

马王爷（星君，第 22 章标题）｜安吉丽娜（星君）｜辰君（星君•黑帮头目）｜吕明｜大金牙｜**宁飞**（早期反派打手，85 次/18 章，首 3）｜**烟头儿**（富老大心腹跟班，157 次/38 章，首 4）｜**张擂**（48 次；自然卷、额前超人式小卷毛）；（太上老君待核：本人 or 药童冒名）

## 🎭 龙套（文字块，不上 LoRA）

其余低频角色（如二宝 等）——含 **ningfei / ningfei_dad / yantouer** 等已在 `config/illustration.yaml` 注册文描块（ch10 起投产）

## 规范

- 定妆流程：候选 12~20 张（`scripts/gen_audition.py`）→ 拼图质检 → 用户确认 → 数据集 13~16 张 + caption（`scripts/build_dataset.py`）→ 训练（`config/train/<slug>_zimage.yaml`，res768 配方；**指标 = TensorBoard `logging.log_dir`**）
- 新角色外观优先摘原文；无描述则设计并保持全书一致，**回写本文件**
- 数据集与配置命名：`datasets/<slug>/`、`config/train/<slug>_zimage.yaml`、`output/<slug>_zimage_lora_v1/`

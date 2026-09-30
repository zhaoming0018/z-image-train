# 《刘老六传奇》全本配图 · 进度与队列（PROGRESS.md）

> 总排程：`~/.hermes/plans/2026-09-29_122313-liulaoliu-illustration-lora-program.md`  
> 更新：2026-09-30 13:05 ｜ 规则：每章 5~8 张；每 5 章一批交付；只做图 ｜ ⚙ 出图管线 v2 已启用：`queuectl` 队列 + `config/` 外置 + GPU 指标走 Prometheus（prometheus-api-client）+ 日志 loguru + 统计 numpy/scipy + 历史脚本已归档（见队列项 9/11/12/13/14）｜ 🗂 项目已 git 化：ai-toolkit 外部依赖、训练配置在 `config/train/`（项 15）｜ 📹 视频路线调研 → `VIDEO_OPTIONS.md`（只读，未实操；含 §3.0 三家直接对比）｜ 🧪 训练指标 = TensorBoard（项 17；`http://localhost:6006`）｜ 🎉 角色 LoRA **7/7 全齐**（侯/佟 09-30 05:38、曹答 11:31 训成）｜ 🧹 monitor_train 退役：A/B 解析直读日志（项 19）｜ 🧩 scripts 模块化：zconf/comfy_lib 公共库（项 20）｜ ✅ 曹答（caoda）收尾全过：已拷 ComfyUI + 注册 illustration.yaml + 冒烟 ×2 合格（ch15 起投产）｜ 🧭 scripts pathlib 化（项 22）

## 章节进度

| # | 章 | 状态 | 张数 | 备注 |
|---|----|------|-----|------|
| 1 | 第一章 我叫刘老六 | ✅ 已交付 | 5 | 黑老头镜头 = 无 LoRA 时代（见「待标记」） |
| 2 | 第二章 乾坤烧鹅富老大 | ✅ 已交付 | 6 | 富老大/慧铭 = 无 LoRA 时代（见「待标记」） |
| 3 | 第三章 出头 | ✅ 已交付 | 7 | 全 LoRA；重拍 4 景（v2×3+v3×1）|
| 4 | 第四章 来包大中华！！！ | ✅ 已交付 | 6 | 全 LoRA；重拍 3 景（s3_dogs 收敛至 v6）|
| 5 | 第五章 六爷的队伍 | ✅ 已交付 | 6 | 全 LoRA（含 he6tou 秧歌队）；重拍 4 景 |
| 6 | 第六章 神仙？ | ✅ 已交付 | 7 | 全 LoRA；重拍 3 景 |
| 7 | 第七章 蛋疼的仙气儿 | ✅ 已交付 | 5 | 全 LoRA；重拍 3 景（s3_shout 收敛至 v6）|
| 8 | 第8章 (失败) | ⏭ 跳过 | — | 正文仅 42 字存根 |
| 9 | 第九章 仙器 | ✅ 已交付 | 6 | 全 LoRA；重拍 3 景（s1×5版 / s5×4版 / s6×2版）|
| 10 | 第十章 揍你全家 | ✅ 已交付 | 6 | 全 LoRA + 宁飞父子（文描块无 LoRA）；重拍 4 景（s2×3 / s3×5 / s4×3 / s5×2；s3 改「意图化」演出）|
| 11 | 第十一章 胖瘦头陀 | ✅ 已交付 | 5 | 全 LoRA（侯/佟登场）；s1 改「猫眼 POV」3 版收敛 |
| 12 | 第十二章 左青龙右白虎 | ✅ 已交付 | 5 | 全 LoRA；中文「飞短留长」四字渲染成功 |
| 13 | 第十三章 觐见富老大 | ✅ 已交付 | 6 | 全 LoRA + 烟头儿文描块；重拍 5 景（拍桌类改「指纸挨训」意图版） |
| 14 | 第十四章 三店总经理 | ✅ 已交付 | 5 | 全 LoRA + 宁飞文描块；重拍 2 景 |
| 15 | 第十五章 内家高手 | ✅ 已交付 | 5 | **曹答/张擂首登场**（张擂=文描块，待定妆；已加 zhanglei 块）；重拍 4 景 |

## 执行队列（滚动，由上至下）

1. ✅ **[完成 09-29 13:25] 首批定妆 + 数据集**
   - 定妆候选：富老大 16+2 补拍、慧铭 A（戴镜）16、B（无镜）16+4 补拍 → `audition/`（用户已拍板：**慧铭 = 无眼镜 B 版定版**（强调"高度近视"场景才用眼镜版）；**富老大通过**）
   - 质检淘汰：fu10（身份漂移）/fu18（手崩）；hb19（脸崩）；fu19 弱胡子但保留
   - 数据集：**fu6lao 13 张**、**huiming 14 张**（`datasets/`，caption 已写；脚本 `scripts/build_dataset.py`）
2. ✅ **[完成 09-29 16:21] 富老大 LoRA**：2500/2500（3h02m，4.05 s/it，末 loss 0.42）→ `output/fu6lao_zimage_lora_v1/fu6lao_zimage_lora_v1.safetensors`（85MB，已拷 ComfyUI `models/loras/`）
   - 验收：**完整角色块成色合格**（中年/横肉/小胡子/过滤嘴烟全命中；⚠️ 弱提示会年轻化漂移 = 与 l6liu 同特性，出图必须带完整块）；胡子偏弱，v2 优化候选（不阻塞）
   - 受影响旧镜头（ch2）：`s2_boss`/`s3_flatter`，已于 **09-29 18:15 评估** → 见「待标记」（待用户重新规划）
3. ✅ **[完成 09-29 19:24] 刘慧铭 LoRA**：2500/2500（2h49m，4.05 s/it，末 loss 0.366）→ `output/huiming_zimage_lora_v1/huiming_zimage_lora_v1.safetensors`（85MB，已拷 ComfyUI `models/loras/`）
   - 验收：末档样图（街景 ✅ / 肖像勉强 = 弱提示漂移）→ **全块提示词冒烟 ×2 = 合格**（16s/14s；卷发/无镜/旧西装命中；小注：卷发偏湿感）→ 出图必带完整角色块
   - ch2 `s5_cafe`/`s6_drag` 受影响评估完成 → 见「待标记」（两镜均**建议重拍**）
4. ✅ **[完成 09-29 20:10] ch3~7 批出图（5 章 31 张）· 首批「全 LoRA」批（l6liu/huiming/fu6lao/he6tou 链式）**
   - 产出：`ch3/`7 + `ch4/`6 + `ch5/`6 + `ch6/`7 + `ch7/`5 = **31 张定版**（备选 `_vN` 留档；总出图 59 = 31 主 + 28 重拍）
   - 质检重拍：17/31 需重拍（动作/接触类镜头为主）→ v2×17 → v3×5 → v4/v5×4 → v6×2 收敛（钉子户 `ch4_s3_dogs`、`ch7_s3_shout` 各 6 次尝试）；每张过 vision 复检
   - 交付：5 条 QQ 逐章分组推送（`hermes send`，多图 MEDIA，exit=0）；终版大图 `sheets/sheet_ch3~7.png`
   - 脚本：`run_ch3_7_batch.py`（批拍）＋`retake_ch3_7.py`/`retake_v3.py`/`retake_v4.py`（重拍轮）
   - 踩坑：多 LoRA 链脚本内「LoRA 文件名常量」与「角色块变量」**严禁重名**（变量遮蔽 → lora_name 传成描述文本 → 400 校验失败，node_errors 点名）
5. ✅ **[完成 09-30 05:38] 侯少麟 + 佟御辉 LoRA（左青龙/右白虎；第 11 章起登场）**
   - 定妆：✅ 用户通过（09-29 夜；侯主锚 01/03/11、佟主锚 11/03/16）；发色「稳定态」定版：佟=灰白、侯=谢顶短发；ch11 一次性「七巧板彩发」**不入 LoRA**
   - 数据集：**侯 13 张 / 佟 14 张**；训练链 `zimage-train-batch2`（`train_chain.sh` 串行）——**侯 23:34→02:37（2h51m @4.12 s/it，末 loss 0.378）；佟 02:37→05:38（2h48m @4.05 s/it，末 loss 0.382）；均 rc=0**
   - 收尾：两 `.safetensors`（85MB）已拷 ComfyUI `models/loras/`；**全块冒烟各 2 张验收合格**（侯：高瘦/谢顶/街头风；佟：矮壮/圆脸/灰白染发；含强化重拍版）；TB 两 run 事件在写；冒烟存档 `output/liulaoliu_story/smoke_hs_tyh/`
   - 后续：**ch11 起二人主场可开拍**（先试拍再全批）
6. **[排队] 二批**：马王爷 / 安吉丽娜 / 辰君 / 大金牙 / 吕明（太上老君待核）；边际新增：张擂
7. **[持续]** 每训成新 LoRA → 产出「受影响旧镜头清单」交用户；ch8+ 巡航
8. ✅ **[完成 09-29 18:45·只读调研] 「配图 → 视频」方案调研** → 详见 `VIDEO_OPTIONS.md`
   - 关键发现：本机 8/22~9/2 **实测出过 18 条 MiniMax H3 视频**（5.2s/15.1s、864×480@24fps、AAC 立体声；9/2 更新 i2v 工作流当晚有出片、R2V 两条）→ 本地出片管线现成
   - 路线结论：**H3 = 零下载首选** / Wan2.2 = 补 ~21GB 双专家 / LTX-2.3 = 速度+音频；云端参考：可灵 2.6 ¥0.3/秒起
   - 未做任何实操；等用户拍板形态与下一步（冒烟测试 / 实施计划 / 云试片）
9. ✅ **[完成 09-29 20:30] 出图管线工程化改造（队列化 + 配置外置 + GPU 指标走 Prometheus）**
   - 指标：GPU 汇总不再自采写 CSV——`scripts/gpu_summary.py` 直查 obs Prometheus（nvidia_gpu_*，5s 采样/15d 保留）；`monitor_train.py`、`ab_parse.py`、`ab_suite.sh` 同步改造（`--gpu-csv` 已删）
   - 出图：提示词/参数外置 → `config/illustration.yaml`（角色块 {占位符}/LoRA 注册表）+ `config/scenes/chN.yaml`（ch3~7 已迁移，31 场景）；执行改队列 → `zimage-redis` 容器 + `scripts/queuectl.py`（enqueue/run/worker/status/retry-failed）；按需服务 `systemctl --user start zimage-queue-worker`
   - 实测：GPU 汇总两窗口对照 ✓｜monitor 仿真冒烟 ✓｜队列 E2E 真渲染 1 张（14.1s，跳过后清理）✓｜全程无残留
   - 用法备忘：`cd ~/z-image-train/scripts && /usr/bin/python3 queuectl.py enqueue 8 9 …` → `… worker`；重拍 = `enqueue <章> --only <景> --suffix _v2 --seed N`
10. ✅ **[完成 09-29 20:55] scripts 命令行工具 CLI 迁移 typer（9 个脚本）**
   - 范围：`gpu_summary` / `queuectl` / `monitor_train` / `ab_parse` / `gen_with_lora` / `qc_montage` / `gen_audition` / `build_dataset` / `make_ab_config`；**接口/输出逐一对齐**（ab_suite.sh 与 systemd 单元零改动，全部 `--help` 可用）
   - 环境：系统 `/usr/bin/python3` 已装 `python3-typer 0.9.0 + python3-rich`（apt 清华源）；`qc_montage` 继续走 aitk python（typer 0.27.2）
   - 验收：ab_parse 复跑输出与迁移前**逐字一致**（vram_peak_mb=8520）；队列 E2E 真渲染 1 张（14.1s）+ purge 清理；monitor 冒烟双向（默认 + `--proc-pattern` 风格）；qc_montage 拼图 / gen_with_lora 真渲染 / systemd 单元全部通过
   - 未动：gen_dataset / migrate_scenes / guard_probe（无 CLI 参数）；run_ch* / retake_*（历史批拍，已被队列取代）；*.sh；queue_lib.py（库）
11. ✅ **[完成 09-29 21:00] scripts 日志统一 loguru（9 个文件）**
   - 新增 `scripts/zlog.py`：统一格式 `MM-DD HH:mm:ss | LEVEL | 消息`（非 TTY 自动去色、`ZLOG_LEVEL` 覆盖级别）；**诊断/进度 → stderr，数据产出保持 stdout**（ab_parse 单行、queuectl status/enqueue、monitor 摘要均不变）
   - 转换：monitor_train（events.log 文件格式原样保留）、queuectl（worker 运行日志）、gen_audition、gen_with_lora、build_dataset、make_ab_config、queue_lib（fail() 失败日志 + 提交重试 DEBUG）、ab_parse（异常补 DEBUG）；不动 gpu_summary（无日志）/ qc_montage（单行产出，免 aitk 新依赖）
   - 验收：ab_parse 输出逐字不变（8520/4.24/176.2）✓ ｜ 队列 E2E 真渲染 14.2s→done ✓ ｜ 失败路径（伪造 LoRA）400 快速拒绝 → 3×DEBUG 重试 + `[FAIL]` 错误日志 ✓ ｜ gen_with_lora 真渲染 14s ✓ ｜ `queue_worker.log` 新行带「时间戳 | 级别」✓ ｜ 无残留
   - 环境：`python3-loguru 0.7.2`（apt 清华源，装进 `/usr/bin/python3`）；**脚本一律 `/usr/bin/python3` 跑**（Hermes 终端裸 `python3` = 工具自带 3.14、缺依赖）
12. ✅ **[完成 09-29 21:25] gpu_summary 改用 prometheus-api-client（查询/解析交给库）**
   - 选型：`custom_query_range`（query_range 正语义、库负责请求构造/状态检查/重试）+ `Metric` 类解析（时间/数值全自动）；**不用** `get_metric_range_data`（其语义为 instant+range-selector 原始采样，与现行 15s 步长网格不同，会改变聚合样本）
   - 验收：**5 组窗口输出与重构前逐字节一致**（fu6lao 8.32GiB@15:44:30/721 · huiming 5.72/641 · 10h 15.07/2401 · 空窗口 · JSON 对比）；ab_parse 复测 8520/4.24/176.2 不变；monitor 冒烟正常；死代理下仍直连成功（trust_env=False ≈ 旧 ProxyHandler({})）
   - 修坑：WSL 未监听端口 = **连接超时**（非拒绝）→ 库默认重试把死端点拖到 60s+；已限界（超时拆 3s 连接/15s 读取 + Retry total=2/connect=1/read=0）→ **6.3s 内降级**出「汇总不可用」、exit 0
   - 环境：apt `python3-pandas 2.1.4` / `dateutil` / `tz` + pip `prometheus-api-client 0.7.2`（清华源，装进 `/usr/bin/python3`）
13. ✅ **[完成 09-29 21:30] 统计计算库化：numpy / scipy（pandas 用于解析层）**
   - `ab_parse`：手写最小二乘回归（mx/my/den 全套手算）→ `scipy.stats.linregress`（斜率倒数 = s/it）；`steps_done` → `np.max`
   - `gpu_summary`：手写 max/sum/sorted 聚合 → numpy（`argmax`/`median`/`mean`/`max`）；中位语义 = **标准中位数**（偶数样本取中间两值均值；已知验收窗口全为奇数，输出不变）
   - `monitor_train`：loss 最低值 → `np.argmin`；**另修自匹配坑**——显式 `--proc-pattern` 出现在监控器自身命令行 → pgrep 假命中自己、监控永不退出 → 结束判定改为**排除自身 PID**（按 ab_suite 调用结构仿真实测 1s 退出；不再依赖"只能用默认探测"的人肉纪律）
   - 验收：fu6lao 复测 `4.24/8520/176.2` 不变（stderr 0 字节）；合成线性数据（60s/10 步）→ `6.0 s/it` 精确、短数据留空；gpu_summary 三窗口（8.32/5.72/15.07）+ `--json` 原生类型；monitor 双路冒烟过
   - 环境：numpy 1.26.4 / scipy 1.11.4 / pandas 2.1.4（系统 `/usr/bin/python3`，apt 已有）
14. ✅ **[完成 09-29 21:40] scripts 目录整理：历史脚本归档（项目外）**
   - 归档至 `~/archive/z-image-train-legacy-20260929/`（11 个文件 1371 行 + `SHA256SUMS.txt` + `MANIFEST.md`）：run_ch2_batch/run_ch3_7_batch（→ `queuectl` 队列 + `config/scenes` 取代）· retake_ch3_7/v3/v4（→ `enqueue --only --suffix --seed` 取代）· gen_dataset（→ `gen_audition`+`build_dataset` 取代）· migrate_scenes_ch3_7（一次性迁移已完成）· guard_probe(.py/_cases.txt)（→ wsl-system-admin 技能维护版取代）· huiming_notify.sh / switch_torch.sh（一次性任务完成）
   - 清理：`scripts/__pycache__` 删除；保留 12 个现行脚本（ab_parse / ab_suite / build_dataset / gen_audition / gen_with_lora / gpu_summary / make_ab_config / monitor_train / qc_montage / queue_lib / queuectl / zlog）
   - 校验：移动前后 sha256 全 OK ｜ 引用扫描（scripts + config + systemd + hermes cron）零残留 ｜ 12 脚本 py_compile 全过 ｜ 冒烟（redis healthy / queue status / gpu_summary）全过
15. ✅ **[完成 09-29 22:00] git 初始化 + ai-toolkit 外部依赖化（训练配置迁出）**
   - 仓库：`~/z-image-train` 已 `git init`（main；首提交 = 脚本/配置/数据集/文档，提交消息中文）；`ai-toolkit/` 整体不入库 = **外部依赖**（pin `ecee894ed2b1f3716d9d7326693061ec1a3105bb`；还原说明见根 `README.md`）
   - 迁出：11 个训练配置 `ai-toolkit/config/` → `config/train/`（l6liu / he6tou / fu6lao / huiming + run4×2；ab_e0/e1/e3/e4/e5 → `config/train/ab/`）；ai-toolkit 恢复纯净（`git status` 除 `__pycache__` 外零文件）
   - 适配：`run_train.sh`（配置绝对路径 + 缺失即报错）· `ab_suite.sh`（CFGD → `config/train/ab`、monitor 特征串 `.*config/train/ab/$cfg`、守护 pgrep 通配）· `make_ab_config.py`（BASE → `config/train/`）· `monitor_train.py`（默认 --proc-pattern → `run.py .*config/train/`）；AB_RUN_PLAN / characters.md 引用同步
   - 入库范围：脚本 / 出图与训练配置 / 数据集（56 图 72.5 MiB + caption + `_manifest.json`）/ 文档（PROGRESS、characters、AB_RUN_PLAN、README）；忽略：ai-toolkit、output 图片与 LoRA、models/wheels/logs/scratch/output_ab、数据集缓存（`_latent_cache` / `_t_e_cache` / `.aitk_size.json`）
   - 验收：7 配置经 ai-toolkit loader 加载 ALL_OK（数据/输出目录存在性）｜ make_ab_config 真实生成 ✓ ｜ `bash -n` ✓ ｜ 迁出 sha256 11/11 OK ｜ 残留引用扫描清零
   - GitHub：SSH 认证可用（zhaoming0018）；首提交 `179393c` 已推送，远程 main 一致
16. ✅ **[完成 09-30 00:10] ch9~10 批出图交付（12 张）**
   - ch9 6 张 + ch10 6 张；全批过 vision 质检；重拍 7 景/11 张（v2×11 → v3×3 → s1 外卡 v4b）
   - 钉子户：ch9 `s1_gifts`（道具+身份，共 5 版收敛到 v2a）、ch10 `s3_poke`（「指尖戳」字面画不出 → **改拍「骚扰意图」**：搭肩+指人+老人畏缩，v4a 定型）
   - 定版规范化执行：主图→`_v1`、定版→主名、备选 `_vN` 全留；命名修正（`giftsv2a`→`gifts_v2a`；**enqueue 的 suffix 必须自带下划线**）
   - 交付：**踩坑修正**——`hermes send` 通道在 QQ 不可达（上报 sent、日志零记录、零送达）→ 已改为随「对话回复 `MEDIA:` 行」补发（该通道有上传记录、可靠）；交付图仍先压缩 jpg q92
17. ✅ **[完成 09-30 00:15] 训练指标接入 TensorBoard（替代日志解析）**
   - 机制：ai-toolkit 原生 `setup_tensorboard`（`SummaryWriter`）→ 训练配置 process 块内 `log_dir: output/.tensorboard` + `logging: {log_every: 25}`（默认 100）；loss/lr 标量按步数写 `<name>_<ts>/` 事件文件
   - 查看：常驻服务 `tensorboard.service`（`~/miniconda3/envs/aitk/bin/tensorboard --logdir output/.tensorboard --port 6006`）→ Windows 浏览器 `http://localhost:6006`（WSL 转发）；重启：`systemctl --user restart tensorboard.service`
   - 注：缺 `tensorboard-data-server`（仅影响网页端部分功能；不影响 PyTorch 写入/读取）；首验：`houshaolin_zimage_lora_v1_20260929-233411/` 事件文件随训练生成 ✓
18. ✅ **[完成 09-30 05:39] 侯/佟训练链监控收尾**：单元哨兵 05:39 捕获链完成（rc=0×2）；03:11 中段守卫已投递（cron 原生通道，agent.log 有 `message_id` 记录）；06:21 收尾守卫已改「独立复核」轻量版（不重做、只核对产物）
19. ✅ **[完成 09-30 08:05] monitor_train.py 退役（A/B 解析改直读训练日志）**
   - 背景：指标已全面 TensorBoard 化（项 17）；常规训练早已不用 monitor，仅 A/B 套件解析链还依赖它
   - 改造：`ab_parse.py` 新增「直读训练日志 tqdm 行」路径（(elapsed, step) 回归，scipy 口径不变；`--metrics-csv` 保留为旧数据回退）；`ab_suite.sh` 移除监控进程，改传 `--window-start/--window-end`（显存/墙钟窗口）
   - 验收：① 兼容路径 4 实验输出**逐字节一致** ② 日志-only 路径与旧值差 ≤0.04 s/it（4.09→4.05 / 11.07→11.1 / 4.04→4.05 / 5.71→5.68）③ 30 步 res768 **真实自测 E2E**：steady 4.07 s/it / vram 5734MB / wall 4.7min（rc=0）④ `bash -n` ✓、TB/单元/产物零残留
   - 归档：`~/archive/z-image-train-legacy-20260929/monitor_train.py`（SHA256SUMS 12/12 复核 OK）；README / AB_RUN_PLAN / 技能（v1.7.0）同步
20. ✅ **[完成 09-30 08:06] scripts 模块化重构（ab_parse 拆分 + 公共库抽取）**
   - `ab_parse.py`：main 拆为 6 个单职责函数（`_read_log` / `_log_fields` / `_speed_points` / `_resolve_window` / `_gpu_peak_mb`），main 仅剩编排（87→33 行）
   - 新增公共库：`zconf.py`（ROOT/CONFIG_DIR/load_yaml/load_specs——路径单源）、`comfy_lib.py`（bridge HTTP 绕代理 / 工作流+LoRA 链 / 提交-轮询-取图——3 处重复实现合并为 1）
   - 调用方全部改走公共库：`queue_lib`（render_job 委派 comfy_lib）、`gen_audition`、`gen_with_lora`、`build_dataset`、`make_ab_config`
   - 验收：① 工作流快照 / ab_parse 兼容路径 / dry-run / 配置生成**逐字节一致** ② 日志路径 s/it 与基线一致（4.05/11.1/4.05/5.68）③ 定妆 71/71 SKIP + manifest md5 未变 + compose 91 条逐字 ④ **真实渲染 E2E ×2**：gen_with_lora 18s、queue 链（3×LoRA）16.2s ⑤ py_compile 全绿、datasets 零变动
21. ✅ **[完成 09-30 11:31] 曹答（caoda）第 7 张 LoRA**：2500/2500 @4.12 s/it、末 loss 0.32（rc=0）→ `output/caoda_zimage_lora_v1/caoda_zimage_lora_v1.safetensors`（85MB，+6 中间档）
   - 收尾（已执行）：① 校验 85MB ② 拷 ComfyUI `models/loras/`（sha256 一致）③ 注册 `illustration.yaml`（loras: caoda + blocks: 曹答完整块，与 dataset 同源）④ 全块冒烟 ×2 合格（肖像 seed42 / 黑轿车场景 seed7；存档 `smoke_caoda/`）⑤ 简报已发；「受影响旧镜头」：无（ch15 才首见）
   - 备注：**ch15 起投产**（出图带完整角色块）；下一棒候选：张擂（48 次·弧 ch15-39）
22. ✅ **[完成 09-30 12:12] scripts pathlib 化（os.path → pathlib，10 文件）**：zconf 的 ROOT/CONFIG_DIR 升级为 Path（路径单源）；join/exists/getsize/makedirs/listdir/splitext/basename 全改 Path 语义（`/`、`.exists()`、`.stat().st_size`、`.mkdir(parents)`、`.iterdir()`、`.stem`）；边界纪律：**进 JSON 的路径保持 str**（队列 job.out_path、render 返回 dst）、sys.path 用 str()；abspath→resolve、`~`→`Path.home()`。未动：gpu_summary/zlog（其 os. 为 os.environ，非路径）。
23. ✅ **[完成 09-30 12:16~12:53] ch11~15 批出图（26 张）· 侯/佟/曹答首次实战 + 张擂首登场**
   - 配置：`illustration.yaml` 注册 `houshaolin`/`tongyuhui` LoRA（此前漏注册）+ 新增 `zhanglei` 文描块；新建 `config/scenes/ch11~15.yaml`（26 场景，seeds 441+/451+/461+/471+/481+）
   - 出图：26 张初版 6 分钟（failed=0）→ 质检直过 9 → 重拍 v2（17 张，seeds 501+）→ 复检 4 过 → v3 收敛轮（13 张，seeds 521+）→ **三轮收敛定版 26 张**（1 张取初版最佳）
   - 定版：规范化完成（主名=定版、`_v1/_v2/_v3` 全留）；`ch11~15_contact_sheet.png` ×5；交付压缩 `_send/`（jpg q92）
   - 交付：✅ 逐章发送完成（ch11~15 五章 26 张全发）；重拍实证已沉淀进 `novel-chapter-illustration` 技能
   - 备注：张擂（ch15 首登场，48 次·弧 ch15-39）为下一棒 LoRA 候选，待用户拍板定妆
   - 验收：py_compile ×12 全绿；--help ×8（含 aitk qc_montage）OK；queuectl status/dry-run、build_dataset 幂等（15/15 SKIP）、ab_parse 单行（steps_done=2500 · steady 4.12 · wall 171.8）、make_ab_config 生成（3 命中）、qc_montage 真拼图（800x912/15 张）、gen_with_lora 真渲染 E2E（16s→1.49MB）—— 全过
24. ✅ **[完成 09-30 13:02] ch15 s2_drive 用户点名重拍 + 老六形象政策调整**
   - 「开车的场景不对」：原图正面摆拍/表情嫌弃 → 改「侧视角 + 惊恐缩身抓安全带」重拍 7 版（v4~v6），v6c 定版（无烟、构图全中）；备选全留
   - 「老六不用时刻都在抽烟」：l6liu / l6liu_new 块默认去烟（illustration.yaml + characters.md 已同步）；需要时场景内显式加回；ch16+ 生效，历史图不回改

## 训练接力 SOP（跨夜训练守卫/收尾通用）

- **常态检查四件套**：① `systemctl --user is-active zimage-train-*`（`--collect` 单元跑完自动卸载，inactive/failed = 已结束）② `logs/train_chain.status`（每配置 START/END rc=…）③ `output/<slug>_zimage_lora_v1/` 产物 ④ `output/.tensorboard/*/` 事件文件
- **接力启动**（前棒成功、后棒未跑）：
  `systemd-run --user --unit=zimage-train-<标签> --collect -p MemoryAccounting=yes -p MemoryMax=18G -p MemorySwapMax=12G -p StandardOutput=append:$HOME/z-image-train/logs/train_<标签>_unit.log -p StandardError=append:$HOME/z-image-train/logs/train_<标签>_unit.log bash -lc 'bash $HOME/z-image-train/scripts/train_chain.sh <cfg1.yaml> [<cfg2.yaml> …]'`
- **失败处理**：读 `logs/train_<slug>.log` 末尾定位；常见：配置找不到、显存被占（`run_train.sh` 会先自动释放 ComfyUI）、OOM（降分辨率/bs）
- **收尾清单**：① 校验最终 `.safetensors`（~85MB）② 拷入 ComfyUI `models/loras/`（`/mnt/d/minimax-h3-demo/ComfyUI/models/loras/`）③ 各跑 1 张**全角色块**冒烟（`gen_with_lora.py` / 队列；先 `unset HTTP_PROXY HTTPS_PROXY ALL_PROXY` + `NO_PROXY=127.0.0.1,localhost`）④ TB events 检查 ⑤ 向用户中文简报（结果/冒烟路径/下一步）
- **纪律**：训练窗口内**一律不出图**；脚本解释器一律 `/usr/bin/python3`；训练进程**严禁挂 Hermes 后台**（4GiB cgroup 硬顶）——必须 systemd 用户单元；完成后向用户给「受影响旧镜头清单」（如有）

## 待标记：无 LoRA 时代镜头（⚑ 用户已拍板：新 LoRA 训成后标记，用户重新规划）

- **ch1**：黑老头戏份镜头（可用 he6tou 重拍评估）
- **ch2 · 富老大（fu6lao）【已评 09-29 18:15】**：`s2_boss`（富老大在背景、中年/小胡子特征弱 → **建议优先重拍**）、`s3_flatter`（中年/横肉/小胡子已命中 → 可保留、重拍可选）→ 已通知用户，待重新规划（**不自动重拍**）
- **ch2 · 慧铭（huiming）【已评 09-29 19:40】**：`s5_cafe`（旧口径：戴眼镜+刺猬头+成色崩坏 → **建议重拍**）、`s6_drag`（戴眼镜+发型不符定版、成色尚可 → **建议重拍**；桥段=网吧"往外拉慧铭"）→ 待用户重新规划（**不自动重拍**）
- 【09-30 05:40】侯少麟/佟御辉：**已训成**（6/6 全齐）——此前章节两人未出场，**无旧镜头需标记**；ch11 起投产
- 【09-30 11:35】曹答：**已训成**（第 7 张）——ch15 才首见、此前无旧镜头需标记；ch15 起投产（出图带完整角色块）
- （新 LoRA 每训成一个，在此追加对应清单并通知用户）
- 【09-29 20:20】fu6lao/huiming 已全面投用（ch3~7 全批实战）；ch2 三镜 `s2_boss`/`s5_cafe`/`s6_drag` **随时可一键重拍**（脚本/角色块就绪）——待用户一句话

## 规则

- 单卡纪律：**训练与出图绝不并发**；出图前 `nvidia-smi` 查空闲；**训练窗口（unit `zimage-train-*` active）= 出图任务一律推迟**，cron 只需汇报状态
- 出图角色**已有 LoRA 必用**（l6liu @0.9、he6tou @0.9、fu6lao/huiming 训成后同样）；未训角色用独立完整文字块（防同脸）
- 训练指标一律看 **TensorBoard**（`output/.tensorboard/`；`http://localhost:6006`），不再从日志解析 loss（项 17）
- 跨夜训练 = systemd 单元 + 后台哨兵 + 一次性 cron 守卫（中段/收尾）；链路/接力见「训练接力 SOP」
- 重 token 任务优先排 **DeepSeek 谷时**（工作日 18:00 后 / 12–14 / 周末与节假日全天）
- cron 批跑：**工作日 18:10、周末 10:05** 自动检查队列并执行（用户喊「暂停批跑」即停）
- 交付 = 图片（无音频）；**交付通道 = 对话回复的 `MEDIA:` 行（`hermes send` 在 QQ 不可达，勿用）**；交付图先压缩（jpg q92）；备选图留在 `chN/` 存档目录
- 重拍规程：判重拍 → 改提示词 + 新 seed（101+ 递增）出 v2；动作/接触类顽固镜头一次出 2 变体择优；≤3 轮收敛；定版规范化 = 原图→`_v1`、定版→主名；`--suffix` 一律**自带下划线**（`_v3a`）
- 脚本：`gen_audition.py`（定妆候选，幂等）、`build_dataset.py`（数据集构建）、`qc_montage.py`（拼图，用 aitk python）、`gen_with_lora.py`（LoRA 出图）、`run_train.sh`（训练启动器）、`train_chain.sh`（串行训练链）；统计/统计量计算统一走 numpy/scipy/pandas（项 13）

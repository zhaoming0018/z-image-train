# A/B 选优 → 双角色 LoRA 训练接力 SOP（l6liu → he6tou）

> 生成：2026-09-29 02:36（A/B 套件运行中）。执行者：Hermes 主会话或守护 cron。
> 本文件是自足的恢复指南：VM 若再崩，恢复后照此执行。
> ⚠️ 2026-09-29 22:00 更新：训练配置已迁出 ai-toolkit → 项目 `config/train/`（ai-toolkit 外部依赖化、不入 git）；下文旧路径 `ai-toolkit/config/...` 一律按 `config/train/...` 替换执行。

## 用户指令
A/B 套件跑完后**直接用最佳配方依次训练两个角色 LoRA**：① l6liu（刘老六）→ ② he6tou（黑老头）。中途无需等用户确认；关键节点向 QQ 汇报。

## 文件与现状
- 套件单元：`zimage-ab-suite`（结果 → `~/z-image-train/logs/ab_runs/AB_SUMMARY.txt`）
- E0 对照基准（已完成）：**steady 5.71 s/it，显存峰值 7308MB，60 步 8.0 分钟**
- E1/E2 已砍（全驻显存组合超 16G 显存容量，且 01:11 曾导致整台 VM 硬崩——永不再试）
- 待出：E3（分辨率 [768,768]，60 步）、E4（batch2，60 步，显存峰值<13.5G 才跑）、E5（150 步验证：E3<5.0s/it 则验证 res768，否则验证对照）
- 训练配置：`config/train/l6liu_zimage.yaml` / `config/train/he6tou_zimage.yaml`（2500 步 / bs1 / resolution [768,1024] / lr 1e-4 / qfloat8 / low_vram+layer_offloading / 每 250 步存档+采样）
- 数据集：`datasets/liu`(15 图)、`datasets/h6tou`(14 图) 均已就绪（注意：配置名为 he6tou、数据集目录名为 h6tou，是同一个角色）
- 启动器：`bash run_train.sh <config>`（内置先 POST :8199/free 释放 ComfyUI 显存）
- 输出：`output/<配置 name>/`；l6liu 旧目录无可用检查点，本次全新开跑（旧 samples_baseline 保留）

## 判定规则（从 AB_SUMMARY.txt 选「最佳」）
先决：只看 ok=1 且 oom=0 的实验行。
1. **E4 batch2 可用** → 折算每样本成本 = s/it ÷ 2，比对照(5.71)快 ≥5%（即 s/it < 10.8）则采用。
   应用：`batch_size: 2`、`steps: 1250`（保持 2500×1 样本曝光量），其余不动。
2. 否则 **E3 res768 可用** → s/it < 5.0 则采用。
   应用：dataset `resolution: [768,768]`，steps 2500 不变。⚠️ 这是降分辨率（训练语义有变），汇报时必须明示。
3. 都不可用 → 用原对照配方直接开跑（已知稳妥）。
4. E5 数据：若其配置与所选一致，作为稳定性佐证；不一致则仅供参考。
5. 若套件异常中断（日志尾部无 AB_SUITE_DONE）：以已完成的实验择优；一个都没有 → 用对照配方直接开跑，并在报告中说明套件异常。

## 执行步骤 A：启动 l6liu

```bash
cd ~/z-image-train
systemctl --user is-active zimage-ab-suite zimage-train-l6liu zimage-train-he6tou   # 应全为 inactive，防重复
cp config/train/l6liu_zimage.yaml config/train/l6liu_zimage_run4.yaml
# 按判定规则编辑 run4 副本（batch2 → batch_size:2 / steps:1250；res768 → resolution [768,768]；name 保持 "l6liu_zimage_lora_v1"）
systemd-run --user --unit=zimage-train-l6liu --collect \
  -p MemoryAccounting=yes -p MemoryMax=18G -p MemorySwapMax=12G \
  -p StandardOutput=append:/home/zhaoyiming/z-image-train/logs/train_l6liu_run4.log \
  -p StandardError=append:/home/zhaoyiming/z-image-train/logs/train_l6liu_run4.log \
  bash -lc 'bash $HOME/z-image-train/run_train.sh l6liu_zimage_run4.yaml'
sleep 15; systemctl --user is-active zimage-train-l6liu; tail -5 logs/train_l6liu_run4.log
```

- 挂完成哨兵（background + notify）：
  `while systemctl --user is-active --quiet zimage-train-l6liu; do sleep 60; done; echo "L6LIU_ENDED $(date +%H:%M)"`
- 指标：常规训练 = TensorBoard；A/B = `ab_parse.py` 直读训练日志（tqdm 行回归，窗口时间戳由套件传入）。~~`scripts/monitor_train.py`~~ 已于 2026-09-30 退役归档（原「服务化监控器」方案废弃）。
- 内存上限依据：量化阶段实测峰值 17.7G RAM + 4.3G swap，18G/12G 为验证过的安全包线。

## 执行步骤 B：l6liu 完成后 → he6tou

```bash
# 检查 l6liu 结果：tail -30 logs/train_l6liu_run4.log；ls output/l6liu_zimage_lora_v1/
cp config/train/he6tou_zimage.yaml config/train/he6tou_zimage_run4.yaml
# 同规则编辑 run4 副本
systemd-run --user --unit=zimage-train-he6tou --collect \
  -p MemoryAccounting=yes -p MemoryMax=18G -p MemorySwapMax=12G \
  -p StandardOutput=append:/home/zhaoyiming/z-image-train/logs/train_he6tou_run4.log \
  -p StandardError=append:/home/zhaoyiming/z-image-train/logs/train_he6tou_run4.log \
  bash -lc 'bash $HOME/z-image-train/run_train.sh he6tou_zimage_run4.yaml'
```

- 挂哨兵：同上（把单元名换成 zimage-train-he6tou）。
- 全部完成后：汇报产物路径（output/*/ 检查点 + 样图），提示用户可复制到 ComfyUI `models/loras/` 出图验证。

## 时间参考
- l6liu：对照配方 ≈4h；batch2(1250步) ≈2.6~3.3h；res768 ≈3~3.5h。
- he6tou 量级相同（14 图）。
- 预计：l6liu ~03:10 开跑 → ~06:00-07:10 完 → he6tou 接续 → 全链 ~09:30-10:30 收尾。

## 纪律（重要）
- 训练/监控一律 systemd 用户单元，**绝不挂 Hermes 后台进程**（4GiB cgroup 硬顶会被 OOM）。
- Hermes 终端护栏写法：pgrep 正则的点写 `\\.`、避免敏感动词组合（详见 wsl-system-admin 技能；A/B 套件曾因此被拦两次）。
- 每步先查状态再动作；启动前必须做防重复检查。
- 这台 VM 有硬崩前科（01:11 崩过一次，宕机 71 分钟）：若再崩，恢复后本文件即是恢复指南。
- 采样默认保留（每 250 步 2 张，进度可视）；极限速度做法是 disable_sampling，本计划不默认采用。

## 收尾任务队列（he6tou 完成后执行，按优先级）
1. **【用户点名】l6liu「不叼烟」出图**：`python3 scripts/gen_with_lora.py smoke_free 42 "l6liu_zimage_lora_v1.safetensors:0.9" "l6liu, a chubby young chinese man, round face, short messy black hair, white ribbed tank top, dark shorts, half body, standing on a small-town street, warm afternoon light, film grain"`（seed 42/7/2026 各出一张选最佳）。
   ⚠️ 数据集几乎每张都叼烟——若换掉 prompt 仍自带烟 = 道具过拟合信号，如实报告；若脸型走样 = 身份绑定偏弱。
2. **一致性对照实验（同 seed 42，特写）× 4**：① 弱描述（复现漂移）`l6liu, portrait close-up, neutral expression, soft window light, film grain` ② 完整块特写 `l6liu, a chubby young chinese man, round face, short messy black hair, white ribbed tank top, portrait close-up, neutral expression, soft window light, film grain` ③ =②+`, cigarette` ④ =②（不叼烟）→ 2×2 拼图发用户，判定身份强度与道具依赖。
3. 拷贝 he6tou LoRA 进 ComfyUI：`cp output/he6tou_zimage_lora_v1/he6tou_zimage_lora_v1.safetensors /mnt/d/minimax-h3-demo/ComfyUI/models/loras/`（l6liu 已提前拷好）。
4. 「有/无 LoRA」同场景对比图（两个角色各一组）→ 最终交付。
5. he6tou 损失曲线图（照 l6liu 的 matplotlib 脚本做）+ 训练总结。

出图工具：`python3 scripts/gen_with_lora.py <输出名> <seed> "<lora文件名>:0.9" "<提示词>"`（经 :8199 桥接→ComfyUI；lora 按文件名从 ComfyUI/models/loras 装载）。**生成前必须确认训练已停、GPU 空闲**（训练期间严禁出图，防崩机）。

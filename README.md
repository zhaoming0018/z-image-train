# z-image-train

Z-Image Turbo 角色 LoRA 训练 + 《刘老六传奇》章节配图工作台（个人项目，WSL 训练节点）。

## 入库内容速览

- `scripts/` — 工具链（typer CLI + loguru）：队列出图 `queuectl`、GPU 汇总 `gpu_summary`、A/B 套件 `ab_suite.sh`（解析直读训练日志，无监控进程）等 11 个现行脚本
- `config/` — 出图配置（`illustration.yaml` + `scenes/chN.yaml`）；**`config/train/` — ai-toolkit 训练配置**（2026-09-29 从 ai-toolkit/config 迁出；A/B 实验配置在 `config/train/ab/`）；`config/datasets/` — 数据集构建规格（`build_dataset.py` 读取：audition_dir / appearance / picks）；`config/auditions/` — 定妆生成规格（`gen_audition.py` 读取：appearance / style / prompts）
- `datasets/` — 角色训练数据集（`ds_*.png` + 同名 `.txt` caption；选择清单见 `config/datasets/`，早期 liu/h6tou 有目录内 `_manifest.json`；ai-toolkit 缓存目录不入库）
- `output/` — 产物目录（图片/LoRA 不入库；`output/liulaoliu_story/` 的 `*.md` 文档与 `index/` 入库）
- `queue/` — 出图队列 Redis 的 docker-compose
- `run_train.sh` — 训练启动器：释放 ComfyUI 显存 → `ai-toolkit/run.py config/train/<名>.yaml`
- 忽略（不入库）：`ai-toolkit/`、`models/`、`wheels/`、`logs/`、`scratch/`、`output_ab/`、数据集缓存（`_latent_cache` / `_t_e_cache` / `.aitk_size.json`）

## 外部依赖

- **ai-toolkit**（训练器，上游 [ostris/ai-toolkit](https://github.com/ostris/ai-toolkit)）：本机路径 `ai-toolkit/`，**不在本仓库跟踪**。
  - 锁定版本：`ecee894ed2b1f3716d9d7326693061ec1a3105bb`（2026-09-29 时点，训练验证通过）
  - 重建：`git clone https://github.com/ostris/ai-toolkit.git && git -C ai-toolkit checkout ecee894`（clone 需代理）
  - 训练配置无需复制回 ai-toolkit——已迁至 `config/train/`，由 `run_train.sh` 以绝对路径传给 `run.py`
- 模型权重（`models/`：Z-Image Turbo 训练适配器等）与 ComfyUI 侧模型：不入库；来源与放置见 Hermes 技能 `z-image-lora-training`

## 约定

- 提交消息用**中文**；代码改动完成后提交。
- 单卡纪律：训练与出图**绝不并发**。
- 细节流程见 Hermes 技能 `z-image-lora-training` / `novel-chapter-illustration`

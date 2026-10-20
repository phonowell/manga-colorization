# 快速开始

## 安装与兼容性

本仓库使用 `SKILL.md` 的 Agent Skills 格式。推荐通过 Skills CLI 安装，它负责将技能放到目标 agent 的目录。Node.js 需要22.20或更高版本。

在你自己的漫画项目目录运行：

```sh
npx skills add phonowell/manga-colorization --skill manga-colorization -a codex
npx skills list -a codex
```

开启新会话，再输入 `$manga-colorization`。需要用户级安装时给安装命令加 `-g`，检查时也加 `-g`。

| 方式 | 能说明什么 | 仍需什么 |
| --- | --- | --- |
| Skills CLI，目标 `codex` | 安装器发现并复制技能资源 | Codex会话与可用生图能力 |
| Skills CLI，目标 `claude-code` | 安装器支持这个目标 | 实际工具接入与效果验证 |
| 手动安装 | 将完整技能目录放入agent认可的位置 | 按你的agent文档确认位置并重新载入 |
| 直接运行Python工具 | 本地诊断和请求准备 | Python依赖及符合格式的输入 |

不想使用Node.js时，从GitHub下载仓库，保留目录结构，放入agent支持的技能目录。不要只复制 `SKILL.md`，它还引用 `references/` 和 `scripts/`。旧的 `~/.codex/skills` 安装如已能发现无需重复安装；新安装优先使用安装器选择的路径。

Skill指令本身不依赖Python。只有运行本地工具时才需安装 `requirements.txt`。生成器不随仓库安装；它需要接受黑白原稿和实际配色参考，而不是只有纯文本生图。

## 完成第一张页面

1. 提供清晰黑白原稿；保留原文件，不先缩放或覆盖。
2. 有则提供官方彩图、已选前页、角色或道具配色，并说清期望风格。
3. 请agent先处理一页，核对输入角色和图像顺序，设置候选数量及停止条件。
4. 用原稿生成，保存原始输出。原尺寸核看文字、表情、眼形、手势、配色归属与整页观感。
5. 让你选择候选；记录实际版本与反馈。未选版前不把agent核看等同于用户批准。

可直接复制[首张上色提示词](../examples/README.md#第一张上色)。单页任务只记录必要的来源、SHA、配色与选择，不必先创建完整章节账本。跨页任务再逐步补上稳定身份、服装状态和配色连续性记录。

如果agent没有生图工具，它可以整理原稿、配色和有效提示词，并说明缺少的接入；不能把核看图、脚本执行或请求准备称为已经上色。

## 先验证本地环境

在仓库工作副本中运行：

```sh
python -m pip install -r requirements.txt
python scripts/quickstart.py --demo --out outputs/first-demo
```

这个命令创建黑白几何测试图及其偏移副本，随后运行现有核看和保真工具。它不绘制漫画，不进行上色，也不联网请求模型。产物包括：

| 路径（相对输出目录） | 用途 |
| --- | --- |
| `inspection/contact-sheet.png` | 原图与候选并排查看 |
| `fidelity/comparison/overview-inspection.png` | 原图、偏移候选、边缘代理诊断 |
| `fidelity/comparison/report.json` | 固定坐标测量与未核状态 |
| `quickstart.json` | 输入SHA、产物入口、零调用及未批准状态 |

输出必须是新目录。诊断图只供核看，不回灌生图或当作交付彩图。它证明本地工具可运行，不证明漫画上色质量。

## 排障

| 现象 | 处理 |
| --- | --- |
| 安装后找不到skill | 开新会话；运行 `npx skills list -a codex`，核对安装scope和agent |
| 不知道如何接生图 | 使用agent已有授权的图像编辑能力，确认支持原稿和参考图输入；仓库不提供Provider |
| `Missing dependency` 或模块导入失败 | 用运行脚本的同一个Python执行 `python -m pip install -r requirements.txt`；建议使用独立环境 |
| 输出目录存在 | 换一个新目录，保留旧证据；不要覆盖旧核看结果 |
| 图片尺寸不同 | 快速入口拒绝自动对齐或缩放；确有预声明padding时使用[高级方案](../references/pixel-fidelity.md) |
| EXIF旋转或透明图被拒 | 先明确方向和透明区域含义，保留原文件及转换记录，再准备不含歧义的输入 |
| 诊断未通过或显示 `unverified` | 原尺寸核看；异常指标和人工画质决定分别记录，不能自动降低阈值 |
| 色好看但字、眼形或手改变 | 拒绝该处内容改变；从原稿返工或选择合格完整分格 |

仍有问题可提交[缺陷报告](https://github.com/phonowell/manga-colorization/issues/new?template=bug_report.yml)。提供脱敏命令、版本、预期和实际结果即可；不必上传私有漫画或完整日志。

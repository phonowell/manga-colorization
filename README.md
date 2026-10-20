# Manga Colorization · 漫画上色

为现有漫画上色与返工的 Codex skill。保留原画、文字、表情和演出，维护角色、服装与道具的跨页配色连续性，区分技术检查、人工画质判断和用户批准。

## 安装与使用

将本仓库克隆到 Codex 的技能目录（已有同名目录时先检查，避免覆盖）：

```sh
gh repo clone phonowell/manga-colorization ~/.codex/skills/manga-colorization
```

在新的 Codex 会话中使用 `$manga-colorization`，例如：

> 使用 $manga-colorization 给这一页漫画上色，保留原稿文字和表情，参照前页保持配色连续。

入口为 [SKILL.md](SKILL.md)，详细流程按需读取 [references/](references/)。`agents/openai.yaml` 提供中文界面元数据。

## 方法边界

- 结构输入来自黑白原稿，可使用整页或完整分格拼版；彩图只作配色参考，不连续编辑上一轮彩图。
- 物体上色、漏色和串色修正交给生图模型，不使用代码蒙版填色或像素重染。
- 允许多候选、完整分格拆回与选优拼接、整格统一调色，保留源 SHA、坐标和处理参数。
- 保真检查使用固定原稿坐标；指标用于定位核看，不能自动批准画质或覆盖用户决定。

## 本地工具

Python 3 环境中按需安装 `requirements.txt`。这两个技能原有工具仅需 Pillow：

- `scripts/inspect_bundle.py`：生成绑定原图 SHA 的只读核看包。
- `scripts/prepare_request.py`：整页请求编译与依赖校验。

同时收录技能引用的 Colorleaf 工具：

- `scripts/prepare-panel-model-rework.py`：原稿完整分格拼版请求准备。
- `scripts/check-source-fidelity.py`：固定坐标的保真诊断，需要 Pillow、NumPy、OpenCV。
- `scripts/calibrate-source-fidelity.py`：用用户已接受样本标定诊断范围，需要 NumPy。
- `scripts/test-source-fidelity.py`：本地保真回归，无模型请求。
- `scripts/audit-reading-order.py`：阅读顺序核看材料与候选告警。

请求编译器和阅读审计工具沿用 Colorleaf 的输入格式，具体见 references 和脚本参数；它们不会自动创建项目账本或推断内容语义。技能中提到的 Colorleaf 当前状态、活账本、审核服务以及 Piexl `generate-page.ts` 是原项目集成背景，本仓库不包含这些运行环境。使用者应接入自己的已授权生图工具；此仓库不提供 Provider、凭据或生图调用授权。分格编译器保留原有模型字段，接入其他运行器时需核对其格式和能力。

运行本地保真回归：

```sh
python scripts/test-source-fidelity.py
```

## 来源

从 Colorleaf 提取。原技能和所引用工具均保持来源文件原始字节，来源提交、路径与逐文件 SHA-256 记录在 [SOURCE.json](SOURCE.json)。不包含漫画图片、私有账本、用户反馈、生成结果、Provider 配置或凭据。

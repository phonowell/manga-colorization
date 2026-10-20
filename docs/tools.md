# 本地工具与适配边界

以下命令在仓库根目录执行，Python 3.10+，依赖见 `requirements.txt`。所有工具均为本地文件处理，不调用图像Provider。脚本的 `--help` 可查看参数。输入、输出的SHA只绑定文件，不证明画质或用户批准。

| 工具 | 最短入口 | 范围 |
| --- | --- | --- |
| `scripts/quickstart.py` | `python scripts/quickstart.py --demo --out outputs/demo` | 自动生成诊断方案并串联核看、保真工具 |
| `scripts/inspect_bundle.py` | `python scripts/inspect_bundle.py --plan plan.json --out outputs/inspection` | 原尺寸裁图、并排核看、SHA清单；需要Pillow |
| `scripts/check-source-fidelity.py` | `python scripts/check-source-fidelity.py --plan plan.json --out outputs/fidelity` | 固定坐标边缘代理、局部定位；需要Pillow、NumPy、OpenCV |
| `scripts/calibrate-source-fidelity.py` | `python scripts/calibrate-source-fidelity.py --help` | 从预先分组的用户已接受样本拟合参考范围；需要NumPy |
| `scripts/prepare_request.py` | `python scripts/prepare_request.py prepare --packet packet.json --out outputs/request` | Colorleaf整页准备格式的原稿、事实和依赖校验 |
| `scripts/prepare-panel-model-rework.py` | `python scripts/prepare-panel-model-rework.py --packet packet.json --out outputs/panels` | Colorleaf格式的完整原稿分格拼版请求准备 |
| `scripts/audit-reading-order.py` | `python scripts/audit-reading-order.py --help` | Colorleaf阅读账本的本地核看材料与候选告警 |

## 使用自己的图片

```sh
python scripts/quickstart.py --source original.png --candidate candidate.png --out outputs/my-review
```

要求两张图片同尺寸、方向明确且不含未解释透明度。无需手写JSON。快速入口不会缩放、配准或处理padding；需要padding声明、关键区域或其他高级参数时，参考生成的两个方案及[保真规则](../references/pixel-fidelity.md)。报告包括本地绝对路径，分享前检查。

快速入口出现运行中断时保留部分产物用于排查；修好原因后使用新目录重跑，未生成 `quickstart.json` 的部分目录不代表完成。

## Colorleaf适配器

`prepare_request.py`、`prepare-panel-model-rework.py` 和 `audit-reading-order.py` 沿用原项目的数据结构。它们适合已有对应账本和准备格式的使用者，不是新用户的必经步骤。整页适配器默认要求真实前页，章节首张可按文档显式使用source-only模式；不应伪造前页。格式及限制见[请求准备](../references/request-packet.md)和[阅读校审](../references/ledger-review.md)。

仓库不包含Colorleaf活账本、审核服务或Piexl运行器。分格编译器保留原有 `model` 字段；接入自己的运行器时检查模型、格式和能力，不把准备成功当作授权、任务已提交或画质合格。

## 本地验证

```sh
python scripts/test-source-fidelity.py
python -m unittest discover -s tests -v
```

测试使用合成输入，不发收费请求。CI运行同一套测试及离线演示。测试验证文件、坐标和入口行为，无法替代真实漫画的语义与审美核看。

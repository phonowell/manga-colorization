# Contributing

欢迎改善首次使用、真实问题诊断和可复现工具行为。中文或英文Issue、PR均可。

## Report a problem

使用[缺陷模板](https://github.com/phonowell/manga-colorization/issues/new?template=bug_report.yml)，提供安装方式、agent/Python版本、脱敏命令、预期和实际结果。尽可能使用合成输入；图片仅在有权公开且不含私有材料时提交。不要上传凭据、Provider完整响应或用户私有账本。

## Make a change

1. Fork并创建工作分支，保持改动范围明确。
2. 保留技能核心约束：原稿结构、模型上色、完整分格处理、来源与用户决定可追溯。
3. 更改脚本时运行相关测试；文档改动核对命令和链接。
4. 说明改变的行为、复现方法和实际运行的验证。

本地验证：

```sh
python -m pip install -r requirements.txt
python scripts/test-source-fidelity.py
python -m unittest discover -s tests -v
python scripts/quickstart.py --demo --out outputs/contribution-demo
```

不要为常规PR发收费生图请求。若改动涉及上色表现，用有权使用的样本说明已核和未核范围，保留失败，不以技术成功代替用户批准。

## Provenance and scope

`SOURCE.json` 中的SHA记录初始提取字节，不应为了匹配后续修改而回填历史SHA。对来源文件的适配在 `adaptedFiles` 中说明。独立仓库不自动回写Colorleaf。

PR中的代码和文档以仓库 [MIT许可证](LICENSE) 提供。若新增第三方内容，保留其来源和许可证，不将漫画使用权与工具许可证混淆。

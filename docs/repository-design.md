# 仓库建设依据与验证范围

调研日期：2026-10-20。通过GitHub API读取README、目录和star数量；star是关注度参考，不是能力评分，也不能证明本技能与其效果相同。

| 参考仓库 | 当日stars | 采纳的建设方式 |
| --- | ---: | --- |
| [obra/superpowers](https://github.com/obra/superpowers) | 302,327 | 显著安装入口、首次触发说明、排障、贡献与测试 |
| [anthropics/skills](https://github.com/anthropics/skills) | 182,357 | 自包含skill、用途说明、标准目录与明确许可范围 |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | 32,692 | 一条安装命令、何时使用、可复制任务示例、渐进文档 |
| [openai/skills](https://github.com/openai/skills) | 28,184 | 安装后重新载入与来源清楚；当前README已标记deprecated，不照搬为新推荐入口 |

安装参数依据 [Skills CLI命令文档](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) 与[发现规则](https://github.com/vercel-labs/skills/blob/main/docs/creating-skills.md)。调研时CLI版本1.7.4，README要求Node.js22.20+。OpenAI官方skills页面本次访问返回403，未据未获取正文声称核对通过；安装发现以实际CLI验证为准。

## 本轮落实

中文首页和英文README；项目级安装、兼容性边界；首张上色、连续页、返工与只核看示例；不依赖私有数据的离线诊断入口；工具说明、排障、MIT、贡献流程、Issue/PR模板和跨平台CI。

保持原稿结构、模型涂色、完整分格处理及固定坐标核看的核心规则。Colorleaf格式适配器作为高级工具，不要求首次使用者先重建其私有运行环境。

诊断预览来自 `scripts/quickstart.py --demo` 的几何测试图。它仅展示诊断产物，不是上色画廊、模型输出或真实漫画效果。未将本地漫画素材搬到公开仓库。

## 能证明与不能证明什么

本地测试可证明入口运行、输入不变、SHA绑定、旧证据不覆盖和固定坐标诊断行为。安装发现和隔离安装验证只能证明技能被安装器识别和资源完整。

CI状态以Actions实际结果为准。安装器支持的agent不自动成为已经实测的生图平台；真实文字、表情、语义与审美仍需用实际作品核看。没有为本轮仓库建设发送生图请求。

## 本轮实际本地结果

23项测试通过（18项原有保真回归、5项首次使用入口行为测试），skill打包校验通过。Skills CLI1.7.4在隔离项目中分别复制到Codex和Claude Code目录，资源逐文件哈希一致；从已安装副本运行离线示例成功。以上不包含两个agent内的真实生图效果验证。

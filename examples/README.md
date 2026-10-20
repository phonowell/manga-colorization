# 可直接使用的任务示例

以下路径和风格用于示范，请换成你的实际文件。英文agent也可使用对应自然语言请求。原稿、彩图参考和被审核版本的角色应明确，不互相替代。

## 第一张上色

```text
使用 $manga-colorization 给 ./originals/page-01.png 上色。
./references/ 是配色与纸张质感参考。我要明亮、通透的水彩。
保留原稿的文字、表情、眼形、手势和分格。
先处理这一页，核看后交给我选版。记录原稿和候选的SHA。
```

预期：从原稿生成候选，核看实际结果，交你选择。没有生图接入时说明缺少的能力并保留准备结果。

## 延续前页

```text
使用 $manga-colorization 处理 ./originals/page-02.png。
./selected/page-01.png 是我已选择的前页，仅供配色连续性参考。
延续角色、服装与道具颜色；变化的光照单独处理。
仍从本页黑白原稿生成，核看文字和眼形后给我选版。
```

预期：明确区分本页结构输入和前页配色参考，记录工作配色与未核归属。

## 反馈返工

```text
使用 $manga-colorization 返工 page-02。
原稿是 ./originals/page-02.png；我审核的是 ./candidates/page-02-v1.png。
右下格头发漏色，书页应为白色；保留已经正确的肤色和原稿空白圆眼。
合并这页仍有效的反馈，先检查已有候选是否有可复用的完整分格。
需要生成时从原稿整页或完整分格出发，拼回后检查最终整页。
```

预期：反馈绑定被审核版本；不连续编辑旧彩图，不用代码给头发或书页直接填色。

## 只做核看

```text
使用 $manga-colorization 比较 ./originals/page-02.png 和 ./candidates/page-02-v2.png。
分别列出原画保真、语义归属、连续性、漏色串色与观感问题。
本次不发模型请求，不改选版；给我实际核看范围和未核项。
```

若仅需要本地固定坐标诊断：

```sh
python scripts/quickstart.py --source original.png --candidate candidate.png --out outputs/review-01
```

预期：生成核看材料与风险定位，保留未核状态。指标和agent判断都不等于用户批准。

---
name: text-to-video
description: "文生视频 / 图生视频 — 使用 MiniMax Hailuo 2.3 API 根据文本描述生成短视频。支持 6s/10s，768P/1080P，可选首帧图片驱动。"
version: "1.0.0"
author: openclaw-agent
---

# text-to-video Skill

基于 MiniMax Hailuo 2.3 的文本转视频生成工具。

## 功能

- 🎬 **文生视频** — 文本描述 → MP4 视频
- 🖼️ **图生视频** — 首帧图片 + 文本 → 视频
- ⏱️ 6 秒 / 10 秒，768P / 1080P
- 🔄 异步生成 + 指数退避轮询
- 💡 提示词自动优化（可选关闭）

## 快速开始

```bash
# 1. 配置 API Key
cp config/config.json.example config/config.json
# 编辑 config.json，填入 MiniMax API Key

# 2. 生成视频
python3 scripts/text_to_video.py "一只猫在阳光下打哈欠，光线柔和"

# 3. 指定时长和分辨率
python3 scripts/text_to_video.py "海浪拍打礁石的慢动作" -d 10 -r 768P

# 4. 图生视频（指定首帧）
python3 scripts/text_to_video.py "花朵绽放" -i cover.jpg

# 5. 指定输出路径
python3 scripts/text_to_video.py "日落延时" -o sunset.mp4
```

## 配置

`config/config.json`:

```json
{
  "api_key": "YOUR_MINIMAX_API_KEY",
  "model": "MiniMax-Hailuo-2.3",
  "default_duration": 6,
  "default_resolution": "768P",
  "output_dir": "~/Downloads/shell/work/text_to_video",
  "poll_interval": 5,
  "timeout": 600
}
```

获取 API Key: https://platform.minimaxi.com → 账户管理 → API Key

## 命令行参数

| 参数 | 说明 |
|------|------|
| `prompt` | 视频描述文本（≤2000字符） |
| `-o, --output` | 输出文件路径 |
| `-d, --duration` | 6 或 10 秒（1080P 仅 6s） |
| `-r, --resolution` | 768P 或 1080P |
| `-i, --image` | 首帧图片路径（图生视频） |
| `--no-optimizer` | 禁用提示词优化 |
| `-c, --config` | 配置文件路径 |

## 镜头控制

提示词中可嵌入镜头指令：

| 指令 | 效果 |
|------|------|
| `[Truck left/right]` | 横移 |
| `[Pan left/right]` | 摇镜 |
| `[Push in/Pull out]` | 推拉 |
| `[Pedestal up/down]` | 升降 |
| `[Zoom in/out]` | 变焦 |
| `[Static shot]` | 固定镜头 |
| `[Tracking shot]` | 跟拍 |

示例: `"一个人从远处走来 [Tracking shot], 然后停下微笑 [Static shot]"`

## 故障排除

**API Key 无效**: 检查 config.json 中 api_key 是否正确

**生成超时**: 默认 10 分钟，可在 config 中调整 timeout

**1080P 限制**: 1080P 仅支持 6 秒视频，10 秒需要 768P

# 🎬 text-to-video

> MiniMax Hailuo 2.3 文生视频 / 图生视频
> 版本: v1.0.0

基于 MiniMax Hailuo 2.3 API 的视频生成 Skill。

## ✨ 功能

- 🎬 **文生视频** — 文本描述直接生成 MP4 视频
- 🖼️ **图生视频** — 首帧图片 + 文本描述驱动视频
- ⏱️ 支持 6 秒 / 10 秒时长
- 📐 支持 768P / 1080P 分辨率
- 🎥 支持镜头控制指令
- 🔄 异步生成 + 指数退避轮询
- 💡 提示词自动优化

## 🚀 快速开始

```bash
# 1. 配置
cp config/config.json.example config/config.json
# 编辑 config.json → 填入 MiniMax API Key

# 2. 文生视频
python3 scripts/text_to_video.py "夕阳下海浪拍打礁石的慢动作"

# 3. 图生视频
python3 scripts/text_to_video.py "花朵绽放" -i cover.jpg

# 4. 10秒 768P
python3 scripts/text_to_video.py "一段延时摄影" -d 10 -r 768P
```

## 📋 命令行参数

```
text_to_video.py [-h] [-o OUTPUT] [-d {6,10}] [-r {768P,1080P}]
                 [-i IMAGE] [--no-optimizer] [-c CONFIG]
                 prompt
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `prompt` | 视频描述文本 | 必填 |
| `-o, --output` | 输出文件路径 | 自动生成 |
| `-d, --duration` | 视频时长（秒） | 6 |
| `-r, --resolution` | 分辨率 | 768P |
| `-i, --image` | 首帧图片路径 | 无（文生视频） |
| `--no-optimizer` | 禁用提示词优化 | 启用 |
| `-c, --config` | 配置文件路径 | config/config.json |

## 🎥 镜头控制

| 指令 | 效果 |
|------|------|
| `[Truck left/right]` | 横移 |
| `[Pan left/right]` | 摇镜 |
| `[Push in/Pull out]` | 推拉 |
| `[Pedestal up/down]` | 升降 |
| `[Zoom in/out]` | 变焦 |
| `[Static shot]` | 固定镜头 |
| `[Tracking shot]` | 跟拍 |
| `[Shake]` | 抖动 |

## 🔧 配置

`config/config.json`:

```json
{
  "api_key": "YOUR_MINIMAX_API_KEY",
  "base_url": "https://api.minimax.io/v1",
  "model": "MiniMax-Hailuo-2.3",
  "default_duration": 6,
  "default_resolution": "768P",
  "output_dir": "~/Downloads/shell/work/text_to_video",
  "poll_interval": 5,
  "timeout": 600
}
```

API Key 获取: https://platform.minimaxi.com → 账户管理 → API Key

## 📦 依赖

- `requests` (pip install requests)
- MiniMax API Key

## ⚠️ 注意事项

- 1080P 仅支持 6 秒视频
- 生成时间通常 1-5 分钟
- 下载链接有效期约 24 小时
- 提示词上限 2000 字符

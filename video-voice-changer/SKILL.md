---
name: video-voice-changer
description: "[DEPRECATED] 视频变声处理工具 - voice-changer v1.6.0 已直接支持视频输入，请直接使用 voice-changer"
version: "1.1.1"
author: M.
deprecated: true
superseded_by: voice-changer
---

# ⚠️ DEPRECATED — video-voice-changer

> **此 Skill 已被废弃**，`voice-changer` v1.6.0+ 已直接支持视频输入，
> 无需手动提取音频再合成。请改用：
>
> ```bash
> python3 ~/.claude/skills/voice-changer/scripts/voice_change.py input.mp4 -v female_3
> ```
>
> 功能完全相同，且更简洁、更可靠。

<details>
<summary>点击展开旧版文档（仅供参考）</summary>

> 版本: v1.1.1
> 默认行为: 创建 `输入文件名_vc.后缀`，只有传入 `--overwrite` 才覆盖原视频。

## 概述

video-voice-changer 是一个视频变声处理 skill，它对视频文件中的音频进行变声处理，然后将处理后的音频与原视频重新合并。

## 功能特性

- 视频音频提取与变声
- 复用 voice-changer skill 的配置
- 支持多种声音预设
- 保持原视频质量（仅替换音频）
- 临时文件自动清理
- **默认不覆盖原文件**（创建新文件）

## 使用方法

```bash
# 基本用法（创建新文件: input_vc.mp4）
python3 ~/.claude/skills/video-voice-changer/scripts/video_voice_change.py input.mp4

# 指定声音类型
python3 ~/.claude/skills/video-voice-changer/scripts/video_voice_change.py input.mp4 -v male_deep

# 指定输出文件
python3 ~/.claude/skills/video-voice-changer/scripts/video_voice_change.py input.mp4 -o output.mp4

# 覆盖原视频文件（需加 --overwrite 参数）
python3 ~/.claude/skills/video-voice-changer/scripts/video_voice_change.py input.mp4 --overwrite

# 保留提取的原始音频
python3 ~/.claude/skills/video-voice-changer/scripts/video_voice_change.py input.mp4 --keep-audio

# 查看帮助
python3 ~/.claude/skills/video-voice-changer/scripts/video_voice_change.py --help
```

## 声音预设

直接使用 voice-changer skill 的配置文件中的预设：

- `female_1` - 女声（轻柔）
- `female_2` - 女声（明亮）
- `female_3` - 女声（甜美）
- `male_deep` - 男声（低沉）
- `male_normal` - 男声（正常）
- `child` - 童声
- `robot` - 机器人

- FFmpeg / FFprobe
- Python 3.8+
- voice-changer skill

</details>

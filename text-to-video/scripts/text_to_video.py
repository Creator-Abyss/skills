#!/usr/bin/env python3
"""
MiniMax Hailuo 2.3 文生视频 / 图生视频
使用 MiniMax API 进行文本转视频生成（异步模式）
"""

import argparse
import json
import os
import sys
import time
import requests
from pathlib import Path


def load_config(config_path=None):
    """加载配置文件"""
    if config_path is None:
        script_dir = Path(__file__).parent.parent
        config_path = script_dir / "config" / "config.json"

    if not config_path.exists():
        example = config_path.with_suffix(".json.example")
        if example.exists():
            print(f"请先配置 API Key: cp {example} {config_path}")
            print(f"然后编辑 {config_path} 填入 MiniMax API Key")
        else:
            print("配置文件不存在，请创建 config/config.json")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def submit_task(cfg, prompt, duration, resolution, first_frame=None, prompt_optimizer=True):
    """提交视频生成任务，返回 task_id"""
    api_key = cfg["api_key"]
    base_url = cfg["base_url"]
    model = cfg.get("model", "MiniMax-Hailuo-2.3")

    body = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "prompt_optimizer": prompt_optimizer,
    }

    if first_frame:
        body["first_frame_image"] = first_frame
        print(f"   首帧图片: {first_frame}")

    print(f"   模型: {model}")
    print(f"   时长: {duration}s")
    print(f"   分辨率: {resolution}")
    print(f"   提示词: {prompt[:80]}...")

    resp = requests.post(
        f"{base_url}/video_generation",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=30,
    )
    data = resp.json()

    if data.get("base_resp", {}).get("status_code") != 0:
        msg = data.get("base_resp", {}).get("status_msg", resp.text)
        raise RuntimeError(f"API 错误: {msg}")

    task_id = data["task_id"]
    print(f"   ✅ 任务已提交: {task_id}")
    return task_id


def poll_task(cfg, task_id):
    """轮询任务状态直到完成，返回 file_id"""
    api_key = cfg["api_key"]
    base_url = cfg["base_url"]
    timeout = cfg.get("timeout", 600)

    start = time.time()
    poll_count = 0
    while True:
        elapsed = time.time() - start
        if elapsed > timeout:
            raise TimeoutError(f"生成超时 ({timeout}s)")

        resp = requests.get(
            f"{base_url}/query/video_generation?task_id={task_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        data = resp.json()
        status = data.get("status", "")

        if status == "Success":
            file_id = data.get("file_id", "")
            if not file_id:
                raise RuntimeError("任务成功但未返回 file_id")
            print(f"   ✅ 生成完成!")
            return file_id

        elif status == "Fail":
            msg = data.get("base_resp", {}).get("status_msg", "未知错误")
            raise RuntimeError(f"生成失败: {msg}")

        else:
            delay = min(2 ** poll_count, 30)
            poll_count += 1
            status_text = status or "Queueing"
            print(f"   ⏳ {status_text}... ({elapsed:.0f}s, next poll {delay}s)")
            time.sleep(delay)


def download_video(cfg, file_id, output_path):
    """下载生成的视频文件"""
    api_key = cfg["api_key"]
    base_url = cfg["base_url"]

    resp = requests.get(
        f"{base_url}/file_retrieve?file_id={file_id}",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30,
    )
    data = resp.json()

    if data.get("base_resp", {}).get("status_code") != 0:
        raise RuntimeError(f"获取下载链接失败: {data}")

    download_url = data.get("file", {}).get("download_url", "")
    if not download_url:
        raise RuntimeError("未获取到下载链接")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    video_resp = requests.get(download_url, timeout=120)
    video_resp.raise_for_status()

    output_path.write_bytes(video_resp.content)
    size_mb = len(video_resp.content) / (1024 * 1024)
    print(f"   💾 已保存: {output_path} ({size_mb:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(
        description="MiniMax Hailuo 2.3 文生视频 / 图生视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
声音预设:
  female_1    女声（轻柔）
  female_2    女声（明亮）
  female_3    女声（甜美）⭐ 默认
  male_deep   男声（低沉）
  male_normal 男声（正常）
  child       童声
        """,
    )
    parser.add_argument("prompt", help="视频描述文本（中文/英文）")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=6,
        choices=[6, 10],
        help="视频时长（秒），默认 6s，1080P 仅支持 6s",
    )
    parser.add_argument(
        "-r", "--resolution",
        default="768P",
        choices=["768P", "1080P"],
        help="分辨率，默认 768P",
    )
    parser.add_argument(
        "-i", "--image",
        help="首帧图片路径（图生视频模式）",
    )
    parser.add_argument(
        "--no-optimizer",
        action="store_true",
        help="禁用提示词优化器",
    )
    parser.add_argument(
        "-c", "--config",
        help="配置文件路径",
    )

    args = parser.parse_args()

    if args.duration == 10 and args.resolution == "1080P":
        print("⚠️  1080P 仅支持 6 秒，已调整")
        args.duration = 6

    cfg = load_config(args.config)

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path(cfg.get("output_dir", "~/Downloads")).expanduser()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"video_{timestamp}.mp4"

    print("=" * 50)
    print("🎬 MiniMax Hailuo 2.3 视频生成")
    print("=" * 50)
    print(f"   提示词: {args.prompt[:100]}...")
    print(f"   输出: {output_path}")
    print()

    try:
        # 1. 提交任务
        print("[1/3] 提交生成任务...")
        task_id = submit_task(
            cfg,
            args.prompt,
            args.duration,
            args.resolution,
            first_frame=args.image,
            prompt_optimizer=not args.no_optimizer,
        )

        # 2. 轮询等待
        print("\n[2/3] 等待生成完成...")
        file_id = poll_task(cfg, task_id)

        # 3. 下载视频
        print("\n[3/3] 下载视频...")
        download_video(cfg, file_id, output_path)

        print()
        print("=" * 50)
        print(f"✅ 生成完成: {output_path}")
        print(f"   任务 ID: {task_id}")
        print("=" * 50)

    except KeyboardInterrupt:
        print("\n⚠️  已中断（远程任务仍在进行中）")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

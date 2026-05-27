#!/usr/bin/env python3
"""
YouTube Video Downloader
Downloads videos from YouTube with customizable quality and format options.
"""

import argparse
import os
import shutil
import sys
import subprocess
import json
import time
from pathlib import Path


def get_default_output_dir():
    """Return platform-appropriate default download directory."""
    home = Path.home()
    downloads = home / "Downloads"
    if downloads.exists():
        return str(downloads)
    return str(home)


def check_yt_dlp():
    """Check if yt-dlp is installed, install safely if not."""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    print("yt-dlp not found. Installing...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "yt-dlp"],
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        print("Auto-install failed. Install manually: pip install yt-dlp")
        return False


def check_disk_space(path, required_mb=500):
    """Check if enough disk space is available."""
    try:
        usage = shutil.disk_usage(Path(path).anchor)
        free_mb = usage.free / (1024 * 1024)
        if free_mb < required_mb:
            print(f"Low disk space: {free_mb:.0f} MB free, {required_mb} MB needed")
            return False
        return True
    except Exception:
        return True  # can't check, proceed anyway


def get_video_info(url):
    """Get information about the video without downloading."""
    result = subprocess.run(
        ["yt-dlp", "--dump-json", "--no-playlist", url],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def download_video(
    url,
    output_path=None,
    quality="best",
    format_type="mp4",
    audio_only=False,
    max_retries=3,
):
    """
    Download a YouTube video with retry and resume support.

    Args:
        url: YouTube video URL
        output_path: Directory to save the video (default: ~/Downloads)
        quality: Quality setting (best, 1080p, 720p, 480p, 360p, worst)
        format_type: Output format (mp4, webm, mkv)
        audio_only: Download only audio (mp3)
        max_retries: Max download attempts
    """
    if not check_yt_dlp():
        return False

    if output_path is None:
        output_path = get_default_output_dir()

    os.makedirs(output_path, exist_ok=True)

    if not check_disk_space(output_path):
        return False

    # Build command
    cmd = ["yt-dlp", "--continue", "--no-playlist"]

    if audio_only:
        cmd.extend(
            [
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", "0",
            ]
        )
    else:
        if quality == "best":
            format_string = "bestvideo+bestaudio/best"
        elif quality == "worst":
            format_string = "worstvideo+worstaudio/worst"
        else:
            height = quality.replace("p", "")
            format_string = (
                f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
            )

        cmd.extend(["-f", format_string, "--merge-output-format", format_type])

    cmd.extend(["-o", f"{output_path}/%(title)s.%(ext)s"])
    cmd.append(url)

    print(f"Downloading from: {url}")
    print(f"Quality: {quality}")
    print(f"Format: {'mp3 (audio only)' if audio_only else format_type}")
    print(f"Output: {output_path}\n")

    # Get video info first
    try:
        info = get_video_info(url)
        print(f"Title: {info.get('title', 'Unknown')}")
        duration = info.get('duration', 0)
        if duration:
            print(f"Duration: {duration // 60}:{duration % 60:02d}")
        print(f"Uploader: {info.get('uploader', 'Unknown')}\n")
    except Exception:
        print("Could not fetch video info, proceeding with download...\n")

    # Download with retry
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                wait = 2 ** (attempt - 1)
                print(f"Retry {attempt}/{max_retries} in {wait}s...")
                time.sleep(wait)

            result = subprocess.run(cmd)

            if result.returncode == 0:
                print(f"\nDownload complete!")
                return True
            else:
                print(f"\nDownload failed (exit code {result.returncode})")
                if attempt < max_retries:
                    continue
                return False

        except KeyboardInterrupt:
            print("\nInterrupted. Re-run with same command to resume.")
            return False
        except Exception as e:
            print(f"\nError: {e}")
            if attempt < max_retries:
                continue
            return False

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube videos with customizable quality and format"
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "-o", "--output",
        default=None,
        help=f"Output directory (default: {get_default_output_dir()})",
    )
    parser.add_argument(
        "-q", "--quality",
        default="best",
        choices=["best", "1080p", "720p", "480p", "360p", "worst"],
        help="Video quality (default: best)",
    )
    parser.add_argument(
        "-f", "--format",
        default="mp4",
        choices=["mp4", "webm", "mkv"],
        help="Video format (default: mp4)",
    )
    parser.add_argument(
        "-a", "--audio-only",
        action="store_true",
        help="Download only audio as MP3",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Max download retries (default: 3)",
    )

    args = parser.parse_args()

    success = download_video(
        url=args.url,
        output_path=args.output,
        quality=args.quality,
        format_type=args.format,
        audio_only=args.audio_only,
        max_retries=args.retries,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

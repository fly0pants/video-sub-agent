#!/usr/bin/env python3
import os
import json
from dotenv import load_dotenv
from app.processor import VideoProcessor

def main():
    # 加载环境变量
    load_dotenv()
    
    # 创建一个测试视频信息
    video_info = {
        "path": "test_videos/test.mp4",
        "name": "The Handmaiden",
        "metadata": {
            "title": "The Handmaiden",
            "original_title": "아가씨",
            "imdb_id": "tt4016934",
            "language": "Korean",
            "release_date": "2016-06-01"
        }
    }
    
    # 创建VideoProcessor实例
    processor = VideoProcessor()
    
    # 测试从网络获取多语言字幕
    print("Testing multi-language subtitle download...")
    result = processor._fetch_subtitles_from_web(video_info)
    
    # 打印结果
    if result:
        print("Download successful!")
        print(f"Source type: {result['source_type']}")
        print("Downloaded subtitles:")
        for subtitle in result['subtitles']:
            print(f"  - Language: {subtitle['language']}, Path: {subtitle['content_path']}")
    else:
        print("Failed to download subtitles.")

if __name__ == "__main__":
    main() 
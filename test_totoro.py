#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from app.processor import VideoProcessor

def main():
    # 加载环境变量
    load_dotenv()
    
    # 创建VideoProcessor实例
    processor = VideoProcessor()
    
    # 创建明确的电影信息
    video_info = {
        "path": "/Volumes/Lenovo/日本动画电影【双字幕】/龙猫.mp4",
        "name": "My Neighbor Totoro",
        "metadata": {
            "title": "My Neighbor Totoro",
            "original_title": "となりのトトロ",
            "imdb_id": "tt0096283",
            "language": "Japanese",
            "release_date": "1988-04-16"
        }
    }
    
    print("测试龙猫(My Neighbor Totoro)的多语言字幕下载...")
    
    # 直接调用_fetch_subtitles_from_web方法测试字幕下载
    result = processor._fetch_subtitles_from_web(video_info)
    
    if result:
        print("下载成功!")
        print(f"字幕来源: {result['source_type']}")
        print("下载的字幕:")
        for subtitle in result['subtitles']:
            print(f"  - 语言: {subtitle['language']}, 路径: {subtitle['content_path']}")
    else:
        print("下载失败.")

if __name__ == "__main__":
    main() 
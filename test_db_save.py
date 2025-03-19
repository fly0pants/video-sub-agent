#!/usr/bin/env python3
from dotenv import load_dotenv
from app.processor import VideoProcessor
from app.database.manager import DatabaseManager

def main():
    # 加载环境变量
    load_dotenv()
    
    # 测试数据库保存功能
    print("Testing database save functionality...")
    
    # 创建VideoProcessor实例
    processor = VideoProcessor()
    db_manager = DatabaseManager()
    
    # 创建测试视频信息
    video_info = {
        "path": "test_videos/test.mp4",
        "name": "The Handmaiden",
        "status": "completed",
        "metadata": {
            "title": "The Handmaiden",
            "original_title": "아가씨",
            "imdb_id": "tt4016934",
            "language": "Korean",
            "release_date": "2016-06-01"
        },
        "subtitle_source": "web",
        "subtitles": [
            {
                "language": "en",
                "content_path": "output/subtitles/test_en.srt"
            }
        ]
    }
    
    # 保存到数据库
    saved = db_manager.save_video_info(video_info)
    if saved:
        print("Successfully saved video info to database.")
    else:
        print("Failed to save video info to database.")
    
    # 从数据库获取视频信息
    print("\nRetrieving video info from database...")
    retrieved_info = db_manager.get_video_info("test_videos/test.mp4")
    if retrieved_info:
        print("Successfully retrieved video info:")
        print(f"Path: {retrieved_info.get('path')}")
        print(f"Name: {retrieved_info.get('name')}")
        print(f"Status: {retrieved_info.get('status')}")
        
        # 打印字幕信息
        subtitles = retrieved_info.get('subtitles', [])
        print(f"Number of subtitles: {len(subtitles)}")
        for sub in subtitles:
            print(f"  - Language: {sub.get('language')}, Path: {sub.get('content_path')}")
    else:
        print("Failed to retrieve video info from database.")

if __name__ == "__main__":
    main() 
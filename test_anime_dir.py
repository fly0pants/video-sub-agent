#!/usr/bin/env python3
import os
import sys
import argparse
from dotenv import load_dotenv
from app.processor import VideoProcessor
from pathlib import Path

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='测试视频处理和多语言字幕下载功能')
    parser.add_argument('directory', help='要处理的视频目录路径')
    parser.add_argument('--force', '-f', action='store_true', help='强制重新处理')
    args = parser.parse_args()

    # 加载环境变量
    load_dotenv()
    
    # 目标目录
    target_dir = args.directory
    
    # 检查目录是否存在
    if not os.path.exists(target_dir):
        print(f"错误: 目录 {target_dir} 不存在")
        return 1
    
    print(f"开始处理目录: {target_dir}")
    
    # 创建VideoProcessor实例
    processor = VideoProcessor()
    
    # 获取目录中的视频文件
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov']
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(list(Path(target_dir).glob(f"*{ext}")))
    
    if not video_files:
        print("未找到视频文件")
        return 1
    
    print(f"找到 {len(video_files)} 个视频文件")
    
    # 处理每个视频文件
    for video_path in video_files:
        print(f"\n处理视频: {video_path}")
        try:
            # 如果已处理并且没有使用--force选项，则跳过
            if not args.force and processor.db_manager.is_video_processed(str(video_path)):
                print(f"视频已处理过。使用 --force 选项强制重新处理。")
                
                # 显示已有的字幕信息
                video_info = processor.db_manager.get_video_info(str(video_path))
                if video_info and "subtitles" in video_info and video_info["subtitles"]:
                    print("已有字幕信息:")
                    for sub in video_info["subtitles"]:
                        print(f"  - 语言: {sub.get('language')}, 路径: {sub.get('content_path')}")
                
                continue
            
            # 处理视频并下载字幕
            result = processor.process_video(str(video_path))
            
            # 打印处理结果
            if result.get("status") == "completed":
                print("处理成功!")
                print(f"片名: {result.get('name')}")
                
                if "metadata" in result and result["metadata"]:
                    meta = result["metadata"]
                    print(f"元数据:")
                    print(f"  标题: {meta.get('title')}")
                    print(f"  原始语言: {meta.get('language')}")
                    print(f"  IMDb ID: {meta.get('imdb_id', '未知')}")
                
                print(f"字幕来源: {result.get('subtitle_source', '未知')}")
                
                if "subtitles" in result and result["subtitles"]:
                    print(f"下载的字幕:")
                    for sub in result["subtitles"]:
                        print(f"  - 语言: {sub.get('language')}, 路径: {sub.get('content_path')}")
                else:
                    print("未找到字幕")
            else:
                print(f"处理失败: {result.get('error', '未知错误')}")
        except Exception as e:
            print(f"处理过程中出错: {str(e)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
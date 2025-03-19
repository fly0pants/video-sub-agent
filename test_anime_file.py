#!/usr/bin/env python3
import sys
import argparse
from dotenv import load_dotenv
from app.processor import VideoProcessor

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='测试单个视频的处理和多语言字幕下载功能')
    parser.add_argument('video_path', help='要处理的视频文件路径')
    parser.add_argument('--force', '-f', action='store_true', help='强制重新处理')
    args = parser.parse_args()

    # 加载环境变量
    load_dotenv()
    
    # 创建VideoProcessor实例
    processor = VideoProcessor()
    
    try:
        # 检查视频是否已处理
        if not args.force and processor.db_manager.is_video_processed(args.video_path):
            print(f"视频已处理过。获取现有信息...")
            video_info = processor.db_manager.get_video_info(args.video_path)
            
            print(f"片名: {video_info.get('name')}")
            
            if "metadata" in video_info and video_info["metadata"]:
                meta = video_info["metadata"]
                print(f"元数据:")
                print(f"  标题: {meta.get('title')}")
                print(f"  原始语言: {meta.get('language')}")
                print(f"  IMDb ID: {meta.get('imdb_id', '未知')}")
            
            print(f"字幕来源: {video_info.get('subtitle_source', '未知')}")
            
            if "subtitles" in video_info and video_info["subtitles"]:
                print(f"字幕信息:")
                for sub in video_info["subtitles"]:
                    print(f"  - 语言: {sub.get('language')}, 路径: {sub.get('content_path')}")
            else:
                print("未找到字幕")
                
            if args.force:
                print("使用--force选项重新处理...")
                processor.db_manager.delete_video(args.video_path)
            else:
                return 0
        
        # 处理视频并下载字幕
        print(f"开始处理视频: {args.video_path}")
        result = processor.process_video(args.video_path)
        
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
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
# Video Analysis and Metadata Management System

一个强大的视频分析和元数据管理系统，可以自动提取字幕、识别电影名称、获取电影元数据，并提供便捷的管理界面。

## 功能特点

- 自动提取视频中的字幕（支持内嵌字幕和外部字幕文件）
- 使用 LLM（DeepSeek）智能识别电影名称
- 从 TMDB 和 OMDB 获取电影元数据
- 支持批量处理视频文件
- 提供命令行界面和 Web API
- 支持多语言（包括中文）电影名称识别
- 数据持久化存储

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/fly0pants/video-sub-agent.git
cd video-sub-agent
```

2. 创建并激活虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 安装系统依赖：

```bash
# macOS (使用 Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# 从 https://www.ffmpeg.org/download.html 下载并安装 FFmpeg
```

5. 配置环境变量：
   创建 `.env` 文件并设置以下变量：

```
DEEPSEEK_API_KEY=your_deepseek_api_key
TMDB_API_KEY=your_tmdb_api_key
OMDB_API_KEY=your_omdb_api_key

DATABASE_URL=sqlite:///./videos.db
OUTPUT_DIR=output
SUBTITLE_OUTPUT_DIR=output/subtitles
TEMP_DIR=temp
```

## 使用方法

### 命令行界面

1. 处理单个视频：

```bash
python -m app.cli process "path/to/video.mp4"
```

2. 批量处理目录中的视频：

```bash
python -m app.cli batch "path/to/directory"
```

3. 识别电影名称：

```bash
python -m app.cli recognize "movie filename or partial name"
```

4. 列出已处理的视频：

```bash
python -m app.cli list
```

### Web API

启动 Web 服务器：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API 文档可在 http://localhost:8000/docs 查看。

## 项目结构

```
video-sub-agent/
├── app/
│   ├── api/            # FastAPI 路由和模型
│   ├── database/       # 数据库模型和操作
│   ├── movie_name/     # 电影名称识别
│   ├── subtitle/       # 字幕提取
│   ├── cli.py         # 命令行界面
│   └── main.py        # FastAPI 应用
├── config/
│   └── settings.py    # 配置管理
├── requirements.txt   # 项目依赖
└── README.md         # 项目文档
```

## 开发计划

- [ ] 添加更多字幕提取方法
- [ ] 改进电影名称识别准确度
- [ ] 添加用户界面
- [ ] 支持更多视频格式
- [ ] 添加视频预览功能
- [ ] 支持更多元数据源
- [ ] 添加字幕翻译功能

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

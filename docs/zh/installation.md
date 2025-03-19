---
layout: default
title: 安装指南
lang: zh
ref: installation
---

# 安装指南

## 系统要求

- Python 3.10 或更高版本
- FFmpeg（用于视频处理）
- Git（用于版本控制）

## 分步安装指南

### 1. 安装系统依赖

#### macOS 系统：

```bash
# 如果未安装 Homebrew，先安装它
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 FFmpeg
brew install ffmpeg
```

#### Ubuntu/Debian 系统：

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

#### Windows 系统：

1. 从[官方网站](https://www.ffmpeg.org/download.html)下载 FFmpeg
2. 将 FFmpeg 添加到系统 PATH

### 2. 克隆仓库

```bash
git clone https://github.com/fly0pants/video-sub-agent.git
cd video-sub-agent
```

### 3. 设置 Python 环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS 系统：
source venv/bin/activate
# Windows 系统：
.\venv\Scripts\activate

# 安装 Python 依赖
pip install -r requirements.txt
```

### 4. 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
# API 密钥
DEEPSEEK_API_KEY=your_deepseek_api_key
TMDB_API_KEY=your_tmdb_api_key
OMDB_API_KEY=your_omdb_api_key

# 数据库配置
DATABASE_URL=sqlite:///./videos.db

# 输出目录
OUTPUT_DIR=output
SUBTITLE_OUTPUT_DIR=output/subtitles
TEMP_DIR=temp

# 处理配置
BATCH_SIZE=10
MAX_WORKERS=4

# 日志设置
LOG_LEVEL=INFO
LOG_FILE=app.log
```

将 `your_*_api_key` 替换为您的实际 API 密钥：

- 从 [DeepSeek](https://platform.deepseek.com) 获取 DeepSeek API 密钥
- 从 [TMDB](https://www.themoviedb.org/settings/api) 获取 TMDB API 密钥
- 从 [OMDB](https://www.omdbapi.com/apikey.aspx) 获取 OMDB API 密钥

### 5. 验证安装

```bash
# 测试命令行界面
python -m app.cli --help

# 测试 API 服务器
python -m uvicorn app.main:app --reload
```

## 故障排除

### 常见问题

1. **找不到 FFmpeg**

   - 确保 FFmpeg 已安装并添加到系统 PATH
   - 运行 `ffmpeg -version` 验证安装

2. **API 密钥问题**

   - 验证 `.env` 文件中的所有 API 密钥是否正确
   - 检查 API 密钥权限和配额

3. **数据库问题**

   - 确保项目目录有写入权限
   - 检查 `.env` 文件中的数据库 URL

4. **Python 依赖问题**
   - 尝试升级 pip：`pip install --upgrade pip`
   - 如果批量安装失败，尝试逐个安装依赖

## 下一步

- 阅读[使用指南](./usage)了解如何使用系统
- 运行服务器时查看 [API 文档](http://localhost:8000/docs)
- 加入我们的 [GitHub 讨论](https://github.com/fly0pants/video-sub-agent/discussions)获取帮助

[返回首页](./){: .btn .btn-outline }

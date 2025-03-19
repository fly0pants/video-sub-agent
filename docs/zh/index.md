---
layout: default
title: 视频字幕助手
lang: zh
ref: home
---

# 视频字幕助手

一个强大的视频分析和元数据管理系统，可以自动提取字幕、识别电影名称、获取电影元数据，并提供便捷的管理界面。

[在 GitHub 上查看](https://github.com/fly0pants/video-sub-agent){: .btn .btn-primary }
[English](../){: .btn }

## 功能特点

- **字幕提取**

  - 从视频文件中提取内嵌字幕
  - 支持外部字幕文件
  - 支持多种字幕格式
  - 智能字幕语言检测

- **电影名称识别**

  - 使用 LLM（DeepSeek）智能识别电影名称
  - 支持多语言（包括中文）
  - 处理各种文件名格式
  - 支持批量处理

- **元数据管理**

  - 从 TMDB 和 OMDB 获取元数据
  - 存储电影信息、类型和演员
  - 数据持久化存储
  - 便捷的数据管理

- **用户界面**
  - 命令行界面支持自动化
  - Web API 便于集成
  - 完整的 API 文档
  - 实时处理状态

## 快速开始

1. 克隆仓库：

```bash
git clone https://github.com/fly0pants/video-sub-agent.git
cd video-sub-agent
```

2. 设置 Python 环境：

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

[安装指南](./installation){: .btn .btn-outline }
[使用指南](./usage){: .btn .btn-outline }

## 开发状态

当前版本：1.0.0

### 开发计划

- [ ] 添加更多字幕提取方法
- [ ] 改进电影名称识别准确度
- [ ] 添加用户界面
- [ ] 支持更多视频格式
- [ ] 添加视频预览功能
- [ ] 支持更多元数据源
- [ ] 添加字幕翻译功能

## 参与贡献

我们欢迎各种形式的贡献！您可以：

- 提交 [Issues](https://github.com/fly0pants/video-sub-agent/issues)
- 创建 [Pull Requests](https://github.com/fly0pants/video-sub-agent/pulls)
- 改进文档
- 分享您的想法

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](https://github.com/fly0pants/video-sub-agent/blob/main/LICENSE) 文件。

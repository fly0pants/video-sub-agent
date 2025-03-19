---
layout: default
title: 使用指南
lang: zh
ref: usage
---

# 使用指南

本指南介绍如何使用视频字幕助手进行视频处理、字幕提取和元数据管理。

## 命令行界面 (CLI)

CLI 提供了多个用于视频处理和管理的命令：

### 处理单个视频

```bash
python -m app.cli process /path/to/video.mp4
```

选项：

- `--force`：即使视频已处理过也强制重新处理
- `--no-subs`：跳过字幕提取
- `--no-meta`：跳过元数据获取

### 批量处理多个视频

```bash
python -m app.cli batch /path/to/video/directory
```

选项：

- `--pattern "*.mp4"`：仅处理匹配模式的文件
- `--recursive`：在子目录中搜索视频
- `--workers 4`：并行工作进程数（默认：4）

### 识别电影名称

```bash
python -m app.cli recognize /path/to/video.mp4
```

此命令使用 AI 从视频文件及其内容中识别电影名称。

### 列出已处理的视频

```bash
python -m app.cli list
```

选项：

- `--status processed`：按处理状态筛选
- `--format json`：以 JSON 格式输出
- `--sort-by date`：按处理日期排序

### 初始化数据库

```bash
python -m app.cli init
```

创建必要的数据库表和目录。

## Web API

系统提供了 RESTful API，可与其他应用程序集成。

### 启动 API 服务器

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API 端点

- `POST /api/videos/process`：处理新视频
- `GET /api/videos`：列出所有已处理的视频
- `GET /api/videos/{video_id}`：获取视频详情
- `DELETE /api/videos/{video_id}`：删除视频记录
- `GET /api/health`：检查 API 健康状态

完整的 API 文档在服务器运行时可在 `http://localhost:8000/docs` 查看。

## Web 界面

提供了 Web 界面，方便管理视频和字幕。

### 访问界面

1. 按上述方法启动 API 服务器
2. 在浏览器中打开 `http://localhost:8000`

### 功能

- 上传和处理视频
- 查看处理状态和进度
- 浏览和搜索已处理的视频
- 下载提取的字幕
- 查看和编辑视频元数据
- 管理视频处理队列

## 字幕处理

### 字幕功能

系统支持提取多种格式的字幕：

- SRT（SubRip）
- VTT（Web Video Text Tracks）
- TXT（纯文本）

### 多语言字幕支持

系统现在支持下载多种语言的字幕：

- 自动从元数据中检测电影的原始语言
- 同时下载英文字幕和电影原始语言的字幕
- 将常见语言名称映射为 ISO 639-1 代码（例如，"Korean" → "ko"）
- 支持同一视频的多语言字幕

### 字幕位置

提取的字幕存储在：

```
output/subtitles/
  - movie_name_en.srt  (英文字幕)
  - movie_name_ko.srt  (韩文字幕)
  - movie_name_zh.srt  (中文字幕)
  - 等等
```

### 字幕处理功能

- 自动语言检测
- 硬编码字幕的 OCR 识别
- 时间同步
- 格式转换

## 元数据管理

### 可用元数据

- 电影标题和年份
- 类型和分类
- 导演和演员
- 剧情简介
- IMDb 评分
- 发行日期
- 语言

### 元数据来源

1. 视频文件名分析
2. AI 驱动的内容识别
3. TMDB 和 OMDB API
4. 手动用户输入

### 更新元数据

```bash
# 使用 CLI
python -m app.cli update <video_id> --title "新标题" --year 2024

# 使用 API
curl -X PATCH http://localhost:8000/api/videos/{video_id} \
  -H "Content-Type: application/json" \
  -d '{"title": "新标题", "year": 2024}'
```

## 最佳实践

1. **组织视频文件**

   - 使用一致的命名规则
   - 将视频保存在专用目录中
   - 保持原始文件名

2. **资源管理**

   - 监控提取字幕的磁盘空间
   - 对大型集合使用适当的批处理大小
   - 定期清理临时文件

3. **错误处理**

   - 检查处理错误日志
   - 使用 `--force` 重试失败的提取
   - 保持 API 密钥和凭据的更新

4. **性能优化**
   - 根据 CPU 核心数调整工作进程数
   - 在非高峰时段处理视频
   - 使用 SSD 存储数据库和临时文件

## 故障排除

### 常见问题

1. **字幕提取失败**

   - 验证视频文件是否损坏
   - 检查视频是否有可提取的字幕
   - 尝试不同的提取方法

2. **电影识别问题**

   - 确保视频文件名具有描述性
   - 检查 API 密钥有效性
   - 尝试手动输入元数据

3. **性能问题**
   - 减小批处理大小
   - 检查系统资源
   - 清理临时文件

### 获取帮助

- 查看[常见问题](./faq)
- 查看 [GitHub Issues](https://github.com/fly0pants/video-sub-agent/issues)
- 加入[讨论](https://github.com/fly0pants/video-sub-agent/discussions)

[返回首页](./){: .btn .btn-outline }

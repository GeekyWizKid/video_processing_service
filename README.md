# Video Processing Service

## 项目介绍

**Video Processing Service** 是一个用于自动化视频处理的服务，支持从视频中提取音频、生成字幕并将字幕嵌入到视频中的功能。

该项目利用 FFmpeg 和 Whisper 等开源工具，提供高效、可扩展的处理流程，适用于各种视频和音频处理需求

## 功能特性

* **音频提取：** 从视频中提取音频并保存为 wav 格式，支持自定义采样率
* **字幕生成**：使用 Whisper 模型自动生成字幕，支持中文和其他语言
* **嵌入字幕**：使用 FFmpeg 将生成的字幕嵌入到视频中，生成带有字幕的最终视频文件
* **支持多种格式**：支持常见的视频格式（如 MP4）及音频格式（如 WAV）

## 项目结构

```
video_processing_service/  
├── config/  
│   └── paths.py                # 配置文件，定义文件路径和目录  
├── src/  
│   └── video_processing.py     # 主要的视频处理逻辑  
├── uploads/                    # 上传的视频文件存储目录  
├── outputs/                    # 处理后的文件输出目录  
│   ├── audio/                  # 提取的音频文件  
│   ├── subtitles/              # 生成的字幕文件  
│   ├── frames/                 # 视频帧  
├── app.py                       # Flask API 服务入口  
└── requirements.txt            # 项目的依赖列表  
```

## 安装及运行

### 克隆项目

```bash
git clone https://github.com/GeekyWizKid/video_processing_service.git
```

```bash
cd video_processing_service
```

### 创建虚拟环境并安装依赖

注意：Python 版本 3.9.12，建议使用 Python 虚拟环境来隔离项目依赖。

创建虚拟环境（可以使用 venv 或 conda）

```bash
python -m venv venv
```

#### Mac/Linux

```bash
source venv/bin/activate
```

#### Windows

```bash
venv\Scripts\activate
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置路径

确保项目中的文件路径（如 uploads 和 outputs 文件夹）已创建。

你可以根据需要修改 config/paths.py 文件中的路径配置。

### 运行 Flask 服务

```bash
python app.py
```

**注意：** Flask 服务将在 http://0.0.0.0:5000 启动，你可以使用该服务进行视频上传和处理。

### 使用 API

测试服务，检查服务是否运行

```bash
curl http://127.0.0.1:5000/test
```

### 上传视频并处理

使用 POST 请求上传视频，服务会自动提取音频、生成字幕并将字幕嵌入到视频中。

### 请求示例

```bash
curl -X POST -F "file=@path_to_video.mp4" http://127.0.0.1:5000/upload
```

### 响应示例

```
{
  "message": "视频处理完成",
  "download_url": "/download/85_1734421479_with_subtitles.mp4"
}
```

### 下载处理后的视频

通过下载 URL 获取处理后的文件

```bash
curl -O http://127.0.0.1:5000/download/85_1734421479_with_subtitles.mp4
```

## 依赖

* **Flask**：用于构建 API 服务
* **Whisper**：OpenAI 的自动语音识别模型，用于生成字幕
* **FFmpeg**：用于视频和音频处理

## 贡献

如果你想贡献代码，可以通过以下步骤：

1. Fork 本项目
2. 创建一个新的分支 (git checkout -b feature-branch)
3. 提交更改 (git commit -am 'Add new feature')
4. 推送到分支 (git push origin feature-branch)
5. 创建一个新的 Pull Request

### 贡献者

<a href="https://github.com/GeekyWizKid/video_processing_service/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=GeekyWizKid/video_processing_service" />
</a>
<a href="https://github.com/GeekyWizKid/video_processing_service/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=WyInnovate/video_processing_service" />
</a>

## 许可

该项目遵循 **MIT** 许可协议。

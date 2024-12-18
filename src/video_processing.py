import os
import subprocess
import whisper
from datetime import timedelta
from config.paths import PathConfig

def extract_audio_from_video(video_path, audio_path, sample_rate=44000):
    """从视频中提取音频并保存为 wav 文件"""
    cmd = [
        'ffmpeg', '-i', video_path, '-vn', '-ar', str(sample_rate),
        '-ac', '2', '-b:a', '128k', audio_path
    ]
    subprocess.run(cmd, check=True)

def format_timestamp(seconds):
    """将秒数转换为 SRT 格式的时间戳"""
    td = timedelta(seconds=float(seconds))
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    seconds = td.total_seconds() % 60
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"

def generate_subtitles(audio_path, output_srt_path, language='zh'):
    """使用 Whisper 生成字幕文件"""
    try:
        # 加载 Whisper 模型
        model = whisper.load_model("large-v3")
        result = model.transcribe(audio_path)

        with open(output_srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result["segments"], 1):
                start_time = format_timestamp(segment["start"])
                end_time = format_timestamp(segment["end"])
                f.write(f"{i}\n{start_time} --> {end_time}\n{segment['text'].strip()}\n\n")

        return True
    except Exception as e:
        print(f"生成字幕时出错: {str(e)}")
        return False


# TODO 这个方法暂时只实现到翻译成英文的功能
def generate_subtitles_with_translation(audio_path, output_srt_path, target_language='zh'):
    """使用 Whisper 生成翻译成目标语言的字幕"""
    try:
        # 加载 Whisper 模型
        model = whisper.load_model("large-v3")

        # TODO 使用 Whisper 的内置翻译功能 whisper 暂时只支持翻译成英文,需要接入第三方翻译服务 , 这里不会生效
        print(f"Transcribing and translating audio to '{target_language}'...")
        result = model.transcribe(audio_path, task="translate")

        # 保存翻译后的字幕
        with open(output_srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result["segments"], 1):
                start_time = format_timestamp(segment["start"])
                end_time = format_timestamp(segment["end"])
                text = segment['text'].strip()

                f.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")

        return True
    except Exception as e:
        print(f"生成翻译字幕时出错: {str(e)}")
        return False


def detect_language_in_audio(audio_path):
    """检测音频中的主语言"""
    try:
        # 加载 Whisper 模型
        model = whisper.load_model("large-v3")

        # 转录音频并获取语言信息
        result = model.transcribe(audio_path)

        # 提取检测到的语言
        detected_language = result['language']
        print(f"检测到的语言是: {detected_language}")

        return detected_language
    except Exception as e:
        print(f"检测语言时出错: {str(e)}")
        return None




def embed_subtitles(video_path, subtitle_path, output_path):
    """使用 FFmpeg 将字幕嵌入到视频中"""
    try:
        cmd = [
            'ffmpeg', '-i', video_path, '-vf', f'subtitles={subtitle_path}', '-c:a', 'copy', output_path
        ]
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"嵌入字幕时出错: {str(e)}")
        return False
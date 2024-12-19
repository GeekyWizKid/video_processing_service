import re

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from config.paths import PathConfig
from src.video_processing import extract_audio_from_video, generate_subtitles, embed_subtitles, \
    generate_subtitles_with_translation
import os

app = Flask(__name__)
CORS(app)

def get_unique_filename(directory, filename):
    """
    生成唯一文件名，避免重名文件覆盖
    :param directory: 保存的目录路径
    :param filename: 原始文件名
    :return: 一个不重复的文件名
    """
    base, extension = os.path.splitext(filename)
    # 移除 base 末尾已有的 (数字) 后缀，避免重复叠加
    base = re.sub(r'\(\d+\)$', '', base)

    counter = 1
    new_filename = f"{base}{extension}"
    new_path = os.path.join(directory, new_filename)

    while os.path.exists(new_path):
        counter += 1
        new_filename = f"{base}({counter}){extension}"
        new_path = os.path.join(directory, new_filename)
    return new_filename


@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Server is running'})


@app.route('/upload', methods=['POST'])
def upload_video():
    # 确保相关目录已存在
    PathConfig.ensure_dirs(
        [PathConfig.UPLOAD_DIR, PathConfig.OUTPUT_DIR, PathConfig.AUDIO_DIR, PathConfig.SUBTITLE_DIR])

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # 处理上传文件名，确保唯一性
    unique_filename = get_unique_filename(PathConfig.UPLOAD_DIR, file.filename)
    video_path = PathConfig.get_upload_path(unique_filename)
    file.save(video_path)

    # 从唯一文件名提取稳定的 base 名称（去掉扩展名）
    base = os.path.splitext(unique_filename)[0]

    # 音频提取
    audio_path = PathConfig.get_audio_path(f"{base}.wav")
    extract_audio_from_video(video_path, audio_path)

    # 检查请求中是否包含 translate 参数
    translate_target_language = request.form.get('translate')

    # 生成字幕
    subtitle_path = PathConfig.get_subtitle_path(f"{base}.srt")
    if translate_target_language:
        success = generate_subtitles_with_translation(audio_path, subtitle_path,
                                                      target_language=translate_target_language)
    else:
        success = generate_subtitles(audio_path, subtitle_path)

    if not success:
        return jsonify({'error': '生成字幕时出错'}), 500

    # 获取用户的返回选项
    return_option = request.form.get('return_option', 'video')  # 默认返回视频

    # 处理返回字幕文件或视频文件
    if return_option == 'subtitle':
        # 返回字幕文件的 JSON 格式链接
        return jsonify({
            'message': '字幕文件处理完成',
            'download_url': f'/download/{os.path.basename(subtitle_path)}'
        })
    else:
        # 嵌入字幕并返回视频文件的 JSON 格式链接
        output_video_path = PathConfig.get_output_path(f"{base}_with_subtitles.mp4")
        embed_subtitles(video_path, subtitle_path, output_video_path)

        return jsonify({
            'message': '视频处理完成',
            'download_url': f'/download/{os.path.basename(output_video_path)}'
        })

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # 根据文件扩展名判断是否是字幕文件
    if filename.endswith('.srt'):
        directory = PathConfig.SUBTITLE_DIR
    else:
        directory = PathConfig.OUTPUT_DIR

    return send_from_directory(directory, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
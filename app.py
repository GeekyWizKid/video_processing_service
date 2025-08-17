import re

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from config.paths import PathConfig
from src.video_processing import extract_audio_from_video, generate_subtitles, embed_subtitles, \
    generate_subtitles_with_translation
from src.subtitle_editor import SubtitleEditor
import os
import subprocess

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


@app.route('/burn', methods=['POST'])
def burn_subtitles():
    # 确保请求体是 JSON
    if not request.is_json:
        return jsonify({'error': 'Invalid content type. Please use application/json'}), 400

    # 从 JSON 请求体中获取 'filename'
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400

    # 确保 PathConfig 的目录已经存在
    PathConfig.ensure_dirs(
        [PathConfig.UPLOAD_DIR, PathConfig.OUTPUT_DIR, PathConfig.AUDIO_DIR, PathConfig.SUBTITLE_DIR]
    )

    # 获取上传目录中的视频文件和字幕文件
    video_path = PathConfig.get_upload_path(f"{filename}.mp4")
    subtitle_path = PathConfig.get_subtitle_path(f"{filename}.srt")

    # 检查视频文件和字幕文件是否存在
    if not os.path.exists(video_path):
        return jsonify({'error': f'Video file "{filename}.mp4" not found'}), 404
    if not os.path.exists(subtitle_path):
        return jsonify({'error': f'Subtitle file "{filename}.srt" not found'}), 404

    # 输出带字幕的视频路径
    output_video_path = PathConfig.get_output_path(f"{filename}_with_subtitles.mp4")

    try:
        # 嵌入字幕
        embed_subtitles(video_path, subtitle_path, output_video_path)
    except Exception as e:
        return jsonify({'error': f'Failed to burn subtitles: {str(e)}'}), 500

    # 返回下载地址
    return jsonify({
        'message': '字幕烧录完成',
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

@app.route('/subtitles', methods=['GET'])
def list_subtitles():
    """获取可用的字幕文件列表"""
    try:
        subtitle_dir = PathConfig.SUBTITLE_DIR
        if not os.path.exists(subtitle_dir):
            return jsonify({'files': []})
        
        files = []
        for filename in os.listdir(subtitle_dir):
            if filename.endswith('.srt'):
                files.append(filename)
        
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': f'获取字幕文件列表失败: {str(e)}'}), 500

@app.route('/subtitles/<filename>', methods=['GET'])
def get_subtitles(filename):
    """获取字幕内容用于编辑"""
    subtitle_path = PathConfig.get_subtitle_path(filename)
    
    if not os.path.exists(subtitle_path):
        return jsonify({'error': '字幕文件不存在'}), 404
    
    editor = SubtitleEditor()
    if not editor.parse_srt_file(subtitle_path):
        return jsonify({'error': '解析字幕文件失败'}), 500
    
    return jsonify({
        'subtitles': editor.get_subtitles_data(),
        'filename': filename
    })

@app.route('/subtitles/<filename>', methods=['PUT'])
def update_subtitles(filename):
    """更新字幕内容"""
    if not request.is_json:
        return jsonify({'error': 'Invalid content type. Please use application/json'}), 400
    
    data = request.get_json()
    subtitles_data = data.get('subtitles')
    
    if not subtitles_data:
        return jsonify({'error': '字幕数据不能为空'}), 400
    
    subtitle_path = PathConfig.get_subtitle_path(filename)
    
    try:
        editor = SubtitleEditor()
        # 重建字幕列表
        for subtitle_data in subtitles_data:
            editor.add_subtitle(
                subtitle_data['start_time'],
                subtitle_data['end_time'],
                subtitle_data['text']
            )
        
        if not editor.save_to_srt(subtitle_path):
            return jsonify({'error': '保存字幕文件失败'}), 500
        
        return jsonify({'message': '字幕更新成功'})
        
    except Exception as e:
        return jsonify({'error': f'更新字幕失败: {str(e)}'}), 500

@app.route('/subtitles/validate', methods=['POST'])
def validate_subtitle_time():
    """验证时间格式"""
    if not request.is_json:
        return jsonify({'error': 'Invalid content type. Please use application/json'}), 400
    
    data = request.get_json()
    time_str = data.get('time')
    
    if not time_str:
        return jsonify({'error': '时间字符串不能为空'}), 400
    
    editor = SubtitleEditor()
    is_valid = editor.validate_time_format(time_str)
    
    return jsonify({
        'valid': is_valid,
        'time': time_str
    })

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/editor')
def editor():
    return send_from_directory('static', 'editor.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
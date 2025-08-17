import re
import os
from datetime import timedelta
from typing import List, Dict, Any

class SubtitleEntry:
    def __init__(self, index: int, start_time: str, end_time: str, text: str):
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'text': self.text
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            index=data['index'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            text=data['text']
        )

class SubtitleEditor:
    def __init__(self):
        self.subtitles: List[SubtitleEntry] = []
    
    def parse_srt_file(self, file_path: str) -> bool:
        """解析SRT字幕文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.subtitles = self._parse_srt_content(content)
            return True
        except Exception as e:
            print(f"解析SRT文件失败: {str(e)}")
            return False
    
    def _parse_srt_content(self, content: str) -> List[SubtitleEntry]:
        """解析SRT内容"""
        subtitles = []
        
        # 分割字幕块
        subtitle_blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in subtitle_blocks:
            if not block.strip():
                continue
                
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            try:
                # 解析索引
                index = int(lines[0].strip())
                
                # 解析时间轴
                time_line = lines[1].strip()
                time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', time_line)
                if not time_match:
                    continue
                
                start_time = time_match.group(1)
                end_time = time_match.group(2)
                
                # 解析文本（可能多行）
                text = '\n'.join(lines[2:])
                
                subtitle = SubtitleEntry(index, start_time, end_time, text)
                subtitles.append(subtitle)
                
            except (ValueError, IndexError):
                continue
        
        return subtitles
    
    def get_subtitles_data(self) -> List[Dict[str, Any]]:
        """获取字幕数据"""
        return [subtitle.to_dict() for subtitle in self.subtitles]
    
    def update_subtitle(self, index: int, start_time: str, end_time: str, text: str) -> bool:
        """更新指定字幕"""
        try:
            for subtitle in self.subtitles:
                if subtitle.index == index:
                    subtitle.start_time = start_time
                    subtitle.end_time = end_time
                    subtitle.text = text
                    return True
            return False
        except Exception as e:
            print(f"更新字幕失败: {str(e)}")
            return False
    
    def add_subtitle(self, start_time: str, end_time: str, text: str) -> bool:
        """添加新字幕"""
        try:
            new_index = len(self.subtitles) + 1
            subtitle = SubtitleEntry(new_index, start_time, end_time, text)
            self.subtitles.append(subtitle)
            self._reindex_subtitles()
            return True
        except Exception as e:
            print(f"添加字幕失败: {str(e)}")
            return False
    
    def delete_subtitle(self, index: int) -> bool:
        """删除指定字幕"""
        try:
            self.subtitles = [s for s in self.subtitles if s.index != index]
            self._reindex_subtitles()
            return True
        except Exception as e:
            print(f"删除字幕失败: {str(e)}")
            return False
    
    def _reindex_subtitles(self):
        """重新索引字幕"""
        for i, subtitle in enumerate(self.subtitles, 1):
            subtitle.index = i
    
    def save_to_srt(self, file_path: str) -> bool:
        """保存为SRT文件"""
        try:
            content = self._generate_srt_content()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"保存SRT文件失败: {str(e)}")
            return False
    
    def _generate_srt_content(self) -> str:
        """生成SRT格式内容"""
        content = []
        
        for subtitle in self.subtitles:
            content.append(str(subtitle.index))
            content.append(f"{subtitle.start_time} --> {subtitle.end_time}")
            content.append(subtitle.text)
            content.append("")  # 空行分隔
        
        return '\n'.join(content)
    
    def validate_time_format(self, time_str: str) -> bool:
        """验证时间格式"""
        pattern = r'^\d{2}:\d{2}:\d{2},\d{3}$'
        return bool(re.match(pattern, time_str))
    
    def time_to_seconds(self, time_str: str) -> float:
        """将时间字符串转换为秒数"""
        try:
            time_part, ms_part = time_str.split(',')
            h, m, s = map(int, time_part.split(':'))
            ms = int(ms_part)
            return h * 3600 + m * 60 + s + ms / 1000
        except Exception:
            return 0.0
    
    def seconds_to_time(self, seconds: float) -> str:
        """将秒数转换为时间字符串"""
        try:
            td = timedelta(seconds=seconds)
            hours = int(td.total_seconds() // 3600)
            minutes = int((td.total_seconds() % 3600) // 60)
            secs = td.total_seconds() % 60
            milliseconds = int((secs % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{milliseconds:03d}"
        except Exception:
            return "00:00:00,000"
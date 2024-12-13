import os
import uuid
import subprocess
import json
from typing import Optional, Literal
from typing import Dict, Any

class Crop_settings:
    """素材的裁剪设置, 各属性均在0-1之间, 注意素材的坐标原点在左上角"""

    upper_left_x: float
    upper_left_y: float
    upper_right_x: float
    upper_right_y: float
    lower_left_x: float
    lower_left_y: float
    lower_right_x: float
    lower_right_y: float

    def __init__(self, *, upper_left_x: float = 0.0, upper_left_y: float = 0.0,
                 upper_right_x: float = 1.0, upper_right_y: float = 0.0,
                 lower_left_x: float = 0.0, lower_left_y: float = 1.0,
                 lower_right_x: float = 1.0, lower_right_y: float = 1.0):
        """初始化裁剪设置, 默认参数表示不裁剪"""
        self.upper_left_x = upper_left_x
        self.upper_left_y = upper_left_y
        self.upper_right_x = upper_right_x
        self.upper_right_y = upper_right_y
        self.lower_left_x = lower_left_x
        self.lower_left_y = lower_left_y
        self.lower_right_x = lower_right_x
        self.lower_right_y = lower_right_y

    def export_json(self) -> Dict[str, Any]:
        return {
            "upper_left_x": self.upper_left_x,
            "upper_left_y": self.upper_left_y,
            "upper_right_x": self.upper_right_x,
            "upper_right_y": self.upper_right_y,
            "lower_left_x": self.lower_left_x,
            "lower_left_y": self.lower_left_y,
            "lower_right_x": self.lower_right_x,
            "lower_right_y": self.lower_right_y
        }

class Video_material:
    """本地视频素材（视频或图片）, 一份素材可以在多个片段中使用"""

    material_id: str
    """素材全局id, 自动生成"""
    local_material_id: str
    """素材本地id, 意义暂不明确"""
    material_name: str
    """素材名称"""
    path: str
    """素材文件路径"""
    duration: int
    """素材时长, 单位为微秒"""
    height: int
    """素材高度"""
    width: int
    """素材宽度"""
    crop_settings: Crop_settings
    """素材裁剪设置"""
    material_type: Literal["video", "photo"]
    """素材类型: 视频或图片"""

    def __init__(self, path: str, material_name: Optional[str] = None, crop_settings: Crop_settings = Crop_settings()):
        """从指定位置加载视频（或图片）素材

        Args:
            path (`str`): 素材文件路径, 支持mp4, mov, avi等常见视频文件及jpg, jpeg, png等图片文件.
            material_name (`str`, optional): 素材名称, 如果不指定, 默认使用文件名作为素材名称.
            crop_settings (`Crop_settings`, optional): 素材裁剪设置, 默认不裁剪.

        Raises:
            `FileNotFoundError`: 素材文件不存在.
            `ValueError`: 不支持的素材文件类型.
        """
        path = os.path.abspath(path)
        postfix = os.path.splitext(path)[1].lower()
        if not os.path.exists(path):
            raise FileNotFoundError(f"找不到 {path}")

        self.material_name = material_name if material_name else os.path.basename(path)
        self.material_id = uuid.uuid3(uuid.NAMESPACE_DNS, self.material_name).hex
        self.path = path
        self.crop_settings = crop_settings
        self.local_material_id = ""

        # 使用 FFprobe 获取文件信息
        try:
            ffprobe_cmd = [
                'ffprobe', 
                '-v', 'quiet', 
                '-print_format', 'json', 
                '-show_format', 
                '-show_streams', 
                path
            ]
            
            result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
            media_info = json.loads(result.stdout)

            # 确定素材类型和基本信息
            video_streams = [s for s in media_info.get('streams', []) if s['codec_type'] == 'video']
            image_streams = [s for s in media_info.get('streams', []) if s['codec_type'] == 'image']

            if video_streams and postfix == '.gif':
                import imageio
                gif = imageio.get_reader(path)

                self.material_type = "video"
                self.duration = int(round(gif.get_meta_data()['duration'] * gif.get_length() * 1e3))
                stream = video_streams[0]
                self.width = int(stream.get('width', 0))
                self.height = int(stream.get('height', 0))
                gif.close()
            elif video_streams:
                self.material_type = "video"
                stream = video_streams[0]
                self.width = int(stream.get('width', 0))
                self.height = int(stream.get('height', 0))

                # 持续时间转换为微秒
                duration = float(media_info.get('format', {}).get('duration', 0))
                self.duration = int(duration * 1e6)
            elif image_streams or postfix in ['.jpg', '.jpeg', '.png']:
                self.material_type = "photo"
                stream = image_streams[0] if image_streams else video_streams[0]
                self.width = int(stream.get('width', 0))
                self.height = int(stream.get('height', 0))
                self.duration = 10800000000  # 3小时，与原实现一致
            else:
                raise ValueError(f"输入的素材文件 {path} 没有视频轨道或图片轨道")

        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            raise ValueError(f"无法使用 FFprobe 解析文件: {e}")

    def export_json(self) -> Dict[str, Any]:
        video_material_json = {
            "audio_fade": None,
            "category_id": "",
            "category_name": "local",
            "check_flag": 63487,
            "crop": self.crop_settings.export_json(),
            "crop_ratio": "free",
            "crop_scale": 1.0,
            "duration": self.duration,
            "height": self.height,
            "id": self.material_id,
            "local_material_id": self.local_material_id,
            "material_id": self.material_id,
            "material_name": self.material_name,
            "media_path": "",
            "path": self.path,
            "type": self.material_type,
            "width": self.width
        }
        return video_material_json

class Audio_material:
    """本地音频素材"""

    material_id: str
    """素材全局id, 自动生成"""
    material_name: str
    """素材名称"""
    path: str
    """素材文件路径"""

    duration: int
    """素材时长, 单位为微秒"""

    def __init__(self, path: str, material_name: Optional[str] = None):
        """从指定位置加载音频素材, 注意视频文件不应该作为音频素材使用

        Args:
            path (`str`): 素材文件路径, 支持mp3, wav等常见音频文件.
            material_name (`str`, optional): 素材名称, 如果不指定, 默认使用文件名作为素材名称.

        Raises:
            `FileNotFoundError`: 素材文件不存在.
            `ValueError`: 不支持的素材文件类型.
        """
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"找不到 {path}")

        self.material_name = material_name if material_name else os.path.basename(path)
        self.material_id = uuid.uuid3(uuid.NAMESPACE_DNS, self.material_name).hex
        self.path = path

        # 使用 FFprobe 获取音频文件信息
        try:
            ffprobe_cmd = [
                'ffprobe', 
                '-v', 'quiet', 
                '-print_format', 'json', 
                '-show_format', 
                '-show_streams', 
                path
            ]
            
            result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
            media_info = json.loads(result.stdout)

            # 检查是否有音频流
            audio_streams = [s for s in media_info.get('streams', []) if s['codec_type'] == 'audio']
            video_streams = [s for s in media_info.get('streams', []) if s['codec_type'] == 'video']

            if not audio_streams:
                raise ValueError(f"给定的素材文件 {path} 没有音频轨道")
            
            if video_streams:
                raise ValueError("音频素材不应包含视频轨道")

            # 获取持续时间（转换为微秒）
            duration = float(media_info.get('format', {}).get('duration', 0))
            self.duration = int(duration * 1e6)

        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            raise ValueError(f"无法使用 FFprobe 解析文件: {e}")

    def export_json(self) -> Dict[str, Any]:
        return {
            "app_id": 0,
            "category_id": "",
            "category_name": "local",
            "check_flag": 1,
            "copyright_limit_type": "none",
            "duration": self.duration,
            "effect_id": "",
            "formula_id": "",
            "id": self.material_id,
            "intensifies_path": "",
            "is_ai_clone_tone": False,
            "is_text_edit_overdub": False,
            "is_ugc": False,
            "local_material_id": self.material_id,
            "music_id": self.material_id,
            "name": self.material_name,
            "path": self.path,
            "query": "",
            "request_id": "",
            "resource_id": "",
            "search_id": "",
            "source_from": "",
            "source_platform": 0,
            "team_id": "",
            "text_id": "",
            "tone_category_id": "",
            "tone_category_name": "",
            "tone_effect_id": "",
            "tone_effect_name": "",
            "tone_platform": "",
            "tone_second_category_id": "",
            "tone_second_category_name": "",
            "tone_speaker": "",
            "tone_type": "",
            "type": "extract_music",
            "video_id": "",
            "wave_points": []
        }

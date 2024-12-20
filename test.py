# 导入模块
import os
import pyJianYingDraft as draft
from pyJianYingDraft import Intro_type, Transition_type, trange

def main():
  tutorial_asset_dir = os.path.join(os.path.dirname(__file__), 'readme_assets', 'tutorial')
  # tutorial_asset_next_dir = os.path.join(os.path.dirname(__file__), 'readme_assets', 'tutorial', '5989')

  # 创建剪映草稿
  script = draft.Script_file(1080, 1080) # 1080x1080分辨率

  # 添加音频、视频和文本轨道Ï
  script.add_track(draft.Track_type.audio).add_track(draft.Track_type.video).add_track(draft.Track_type.text)

  # 从本地读取音视频素材和一个gif表情包
  # audio_material = draft.Audio_material(os.path.join(tutorial_asset_next_dir, 'output_audio.mp3'))
  audio_material = draft.Audio_material(os.path.join(tutorial_asset_dir, 'audio.mp3'))
  # video_material = draft.Video_material(os.path.join(tutorial_asset_next_dir, 'output_video.mp4'))
  video_material = draft.Video_material(os.path.join(tutorial_asset_dir, 'video.mp4'))
  # video_material1 = draft.Video_material(os.path.join(tutorial_asset_next_dir, '1.mp4'))
  sticker_material = draft.Video_material(os.path.join(tutorial_asset_dir, 'sticker.gif'))
  # .add_material(video_material1)
  script.add_material(audio_material).add_material(video_material).add_material(sticker_material) # 随手添加素材是好习惯

  # 创建音频片段Ï
  audio_segment = draft.Audio_segment(audio_material,
                                      trange("0s", "3s"), # 片段将位于轨道上的0s-5s（注意5s表示持续时长而非结束时间）
                                      volume=0.6)         # 音量设置为60%(-4.4dB)
  audio_segment.add_fade("1s", "0s")                      # 增加一个1s的淡入

  # 创建视频片段
  video_segment = draft.Video_segment(video_material, trange("0s", "3s")) # 片段将位于轨道上的0s-4.2s（取素材前4.2s内容，注意此处4.2s表示持续时长）
  video_segment.add_animation(Intro_type.斜切)                              # 添加一个入场动画“斜切”
  # 为二者添加一个转场
  video_segment.add_transition(Transition_type.信号故障)  # 注意转场添加在“前一个”视频片段上

  sticker_segment = draft.Video_segment(sticker_material,
                                        trange(video_segment.end, sticker_material.duration)) # 紧跟上一片段，长度与gif一致
  # sticker_segment.add_transition(Transition_type.分割)  # 注意转场添加在“前一个”视频片段上


  # video_segment1 = draft.Video_segment(video_material1, trange(sticker_segment.end, video_material1.duration))


  # 将上述片段添加到轨道中
  script.add_segment(audio_segment).add_segment(video_segment).add_segment(sticker_segment)

  # 创建一行类似字幕的文本片段并添加到轨道中
  text_segment = draft.Text_segment("测试字幕？?", trange(0, script.duration),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    style=draft.Text_style(color=(1.0, 1.0, 0.0)),                # 设置字体颜色为黄色
                                    clip_settings=draft.Clip_settings(transform_y=-0.8))          # 模拟字幕的位置
  script.add_segment(text_segment)

  # 保存草稿（覆盖掉原有的draft_content.json）
  script.dump(r"E:\Software\Jianying\JianyingPro Drafts\test_draft\draft_content.json")
  # script.dump("/Users/baixing_ricky/Movies/CapCut/User Data/Projects/com.lveditor.draft/1212/draft_info.json")

if __name__ == '__main__':
    main()
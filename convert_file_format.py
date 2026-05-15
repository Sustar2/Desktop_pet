#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：desktop_pet 
@File    ：convert_file_format.py
@IDE     ：PyCharm 
@Author  ：XWJ
@Date    ：2026/5/15 16:29 
@Desc    :
"""

from moviepy import VideoFileClip

def convert_mp4_to_gif(mp4_path):
    """
    convert mp4 to gif
    :return:
    """
    #加载你下载的视频文件
    clip = VideoFileClip(mp4_path)

    # 将其保存为 gif
    # fps 可以控制帧率，越大越流畅但文件也越大
    clip.write_gif(mp4_path.replace('.mp4', '.gif'), fps=15)


if __name__ == '__main__':
    convert_mp4_to_gif('../desktop_pet/images/neko1.mp4')
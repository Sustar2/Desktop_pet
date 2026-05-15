#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：desktop_pet 
@File    ：pet.py
@IDE     ：PyCharm 
@Author  ：XWJ
@Date    ：2026/5/15 14:24 
@Desc    :
"""
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        # 1. 准备图片列表和当前索引
        self.image_paths = ["neko1.png", "neko2.png", "neko3.png", "neko4.png"]
        self.current_index = 0  # 默认显示列表里的第 0 张（即 cat1.png）

        self.init_ui()

    def init_ui(self):
        # 设置无边框、永远置顶、不在任务栏显示
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        # 设置窗口背景透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(self)

        # 调用专门提取出来的刷新图片方法
        self.update_image()

        # 初始化记录鼠标拖拽位置的变量
        self._drag_pos = QPoint()

    def update_image(self):
        """专门用来加载和刷新猫咪图片的方法"""
        current_image = self.image_paths[self.current_index]
        pixmap = QPixmap(current_image)

        # 如果需要缩小图片，可以取消下面这行的注释并调整数值
        pixmap = pixmap.scaledToWidth(150, Qt.TransformationMode.SmoothTransformation)

        self.label.setPixmap(pixmap)
        self.label.adjustSize()
        self.resize(self.label.size())

    # --- 鼠标事件监听 ---
    def mousePressEvent(self, event):
        # 当鼠标左键按下时
        if event.button() == Qt.MouseButton.LeftButton:
            # 记录拖动初始位置
            self._drag_pos = event.globalPosition().toPoint()

            # --- 核心修改：切换图片 ---
            # 每次点击，索引 +1。利用取余数 (%) 让索引在 0, 1, 2, 3 之间无限循环
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.update_image()  # 刷新显示

    def mouseMoveEvent(self, event):
        # 拖动窗口逻辑
        if not self._drag_pos.isNull() and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        # 鼠标松开清空记录
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = QPoint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())
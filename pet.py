#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：desktop_pet 
@File    ：pet2.py
@IDE     ：PyCharm 
@Author  ：XWJ
@Date    ：2026/5/15 16:01 
@Desc    :
"""
import sys
import os
import random
import json
import re
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QMenu, QInputDialog
from PyQt6.QtCore import Qt, QPoint, QTimer, QSize
from PyQt6.QtGui import QPixmap, QAction, QMovie

IMAGE_FOLDER='images'
AUX_FOLDER='auxiliary'

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        # 1. 准备图片列表和当前索引
        # 3. 读取 images 文件夹下所有图片
        try:
            # --- 核心修复：添加后缀名过滤，彻底无视 .gitkeep 和其他杂乱文件 ---
            valid_extensions = ('.png', '.jpg', '.jpeg', '.gif')
            image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(valid_extensions)]

            # 再进行排序拼接
            self.image_paths = sorted(
                [os.path.join(IMAGE_FOLDER, p) for p in image_files],
                key=lambda x: int(re.findall(r'\d+', x)[-1]) if re.findall(r'\d+', x) else 0
            )
        except Exception as e:
            print(f"读取图片失败: {e}")
            self.image_paths = []
        self.current_index = 0  # 默认显示列表里的第 0 张（即 cat1.png）

        # 定义配置文件的路径
        self.config_path = os.path.join(AUX_FOLDER, "config.json")

        # 默认名字
        self.pet_name = ""

        # 尝试读取保存的名字
        self.load_config()

        self.init_ui()

    def load_config(self):
        if not os.path.exists(self.config_path):
            self.save_config()
        else:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.pet_name = data.get("pet_name", "小猫咪")
            except Exception:
                self.save_config()

    def save_config(self):
        data_to_save = {"pet_name": self.pet_name}
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

    def init_ui(self):
        # 窗口基础设置
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 【重点】这里改为 image_label，专门承载图片
        self.image_label = QLabel(self)

        if self.image_paths:
            self.update_image()
        else:
            self.image_label.setText("未找到图片")
            self.image_label.setStyleSheet("color: red; font-size: 20px; background-color: white;")
            self.image_label.adjustSize()
            self.resize(self.image_label.size())

        self._drag_pos = QPoint()

        # 初始位置：屏幕 8/10 处
        screen_geo = QApplication.primaryScreen().availableGeometry()
        x = int(screen_geo.width() * 0.8 - self.width() / 2)
        y = int(screen_geo.height() * 0.8 - self.height() / 2)
        self.move(x, y)

    # def update_image(self):
    #     """专门用来加载和刷新猫咪图片的方法"""
    #     if not self.image_paths: return
    #
    #     current_image = self.image_paths[self.current_index]
    #
    #     # 1. 打印它到底在尝试加载哪个绝对路径！
    #     print(f"🔎 正在尝试加载图片路径: {current_image}")
    #
    #     pixmap = QPixmap(current_image)
    #
    #     # 2. 拦截检查：如果加载出来是空的，立刻发出警告
    #     if pixmap.isNull():
    #         print(f"❌ 警告：路径正确，但 PyQt 无法解析这张图片！(可能是格式不对，或缺少图像插件)")
    #         return  # 加载失败就直接停止，防止后面报错
    #
    #     # 如果你取消了下面这行的注释，请确保它放在 isNull 拦截的后面！
    #     pixmap = pixmap.scaledToWidth(150, Qt.TransformationMode.SmoothTransformation)
    #
    #     self.image_label.setPixmap(pixmap)
    #     self.image_label.adjustSize()
    #     self.resize(self.image_label.size())

    def update_image(self):
        """智能加载：自动识别并显示静态图或GIF动图"""
        if not self.image_paths: return

        current_image = self.image_paths[self.current_index]

        # 1. 每次切换前，先“打扫卫生”
        # 如果之前正在播放 GIF，先把它停掉并清理内存，防止两个动画打架
        if hasattr(self, 'movie') and self.movie:
            self.movie.stop()
            self.movie.deleteLater()
            self.movie = None  # 重置为空

        # 2. 智能判断后缀名
        if current_image.lower().endswith('.gif'):
            # =========================
            # 🎬 路线 A：处理 GIF 动图
            # =========================
            self.movie = QMovie(current_image)

            if not self.movie.isValid():
                print(f"❌ 警告：无法解析 GIF 文件: {current_image}")
                return

            # ==========================================
            # 🌟 新增：在这里修改 GIF 的尺寸！
            # 设定你想要的固定宽度（比如 150）
            target_width = 150

            # 让程序先“看”一眼 GIF 的第一帧，以便获取它的原始尺寸
            self.movie.jumpToFrame(0)
            original_size = self.movie.currentImage().size()

            # 如果成功获取到了原始尺寸，就按比例计算出高度，并设置新的尺寸
            if original_size.width() > 0:
                target_height = int(target_width * original_size.height() / original_size.width())
                self.movie.setScaledSize(QSize(target_width, target_height))
            # ==========================================

            self.image_label.setMovie(self.movie)
            self.movie.start()  # 动图必须调用 start 才能播放

        else:
            # =========================
            # 🖼️ 路线 B：处理静态图片
            # =========================
            pixmap = QPixmap(current_image)

            if pixmap.isNull():
                print(f"❌ 警告：无法解析静态图片: {current_image}")
                return

            # 如果需要缩放静态图片，可以在这里加：
            pixmap = pixmap.scaledToWidth(150, Qt.TransformationMode.SmoothTransformation)

            self.image_label.setPixmap(pixmap)

        # 3. 统一调整窗口大小以适应当前显示的图片或动图
        self.image_label.adjustSize()
        self.resize(self.image_label.size())

    def show_bubble(self, text=None):
        # 如果存在旧气泡，先关掉并清理内存
        if hasattr(self, 'bubble') and self.bubble:
            self.bubble.close()
            self.bubble.deleteLater()

        messages = [
            f"我是{self.pet_name}，喵~",
            f"今天也要加油呀，主人！",
            f"点我干嘛？要抱抱吗？",
            f"别摸了，毛都要掉光了...",
            f"我在盯着你写代码哦~"
        ]
        display_text = text if text else random.choice(messages)

        # 独立的气泡窗口
        self.bubble = QLabel(display_text)
        self.bubble.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.bubble.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.bubble.setStyleSheet("""
            QLabel {
                background-color: rgba(30, 30, 30, 200);
                border: 2px solid #FFB6C1;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 14px;
                color: white;
                font-weight: bold;
            }
        """)
        self.bubble.adjustSize()

        # 定位到猫咪头顶
        bubble_x = self.x() + (self.width() - self.bubble.width()) // 2
        bubble_y = self.y() - self.bubble.height() - 10
        self.bubble.move(bubble_x, bubble_y)
        self.bubble.show()

        # 3秒后自动关闭
        QTimer.singleShot(3000, self.bubble.close)

    def showEvent(self, event):
        super().showEvent(event)
        # 延迟显示启动语，确保猫咪坐标已生成
        QTimer.singleShot(200, lambda: self.show_bubble(f"主人，{self.pet_name} 来陪你啦！"))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            if self.image_paths:
                self.current_index = (self.current_index + 1) % len(self.image_paths)
                self.update_image()
            self.show_bubble()

    def mouseMoveEvent(self, event):
        if not self._drag_pos.isNull() and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

            # 让气泡跟着猫咪一起动（如果气泡正在显示的话）
            if hasattr(self, 'bubble') and self.bubble.isVisible():
                bubble_x = self.x() + (self.width() - self.bubble.width()) // 2
                bubble_y = self.y() - self.bubble.height() - 10
                self.bubble.move(bubble_x, bubble_y)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = QPoint()

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        context_menu.setStyleSheet("""
            QMenu { background-color: rgba(30, 30, 30, 200); color: white; border: 1px solid #FFB6C1; border-radius: 5px; }
            QMenu::item { padding: 5px 20px 5px 20px; }
            QMenu::item:selected { background-color: #FFB6C1; color: black; }
        """)

        rename_action = QAction("给宠物改名", self)
        rename_action.triggered.connect(self.change_name_dialog)
        context_menu.addAction(rename_action)

        context_menu.addSeparator()

        quit_action = QAction("退出桌宠", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        context_menu.addAction(quit_action)

        context_menu.exec(event.globalPos())

    def change_name_dialog(self):
        new_name, ok = QInputDialog.getText(self, "修改名字", "请输入宠物的名字：", text=self.pet_name)
        if ok and new_name.strip():
            self.pet_name = new_name.strip()
            self.save_config()
            self.show_bubble(f"好耶！以后我就叫 {self.pet_name} 啦！")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：desktop_pet 
@File    ：pet2.py
@IDE     ：PyCharm 
@Author  ：XWJ
@Date    ：2026/5/15 17:50 
@Desc    :
"""
import sys
import os
import random
import json
import re
import glob
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QMenu, QGraphicsDropShadowEffect, QInputDialog
from PyQt6.QtCore import Qt, QPoint, QTimer, QSize
from PyQt6.QtGui import QPixmap, QAction, QMovie, QCursor, QColor

def resource_path(relative_path):
    """获取打包后资源的绝对路径（只读临时目录）"""
    try:
        base_path = sys._MEIPASS          # PyInstaller 创建的临时目录
    except AttributeError:
        base_path = os.path.abspath(".")  # 开发环境
    return os.path.join(base_path, relative_path)

def get_resource_folder(folder_name):
    """
    优先返回可执行文件同目录下的文件夹（用户可修改），
    如果不存在或为空，则回退到打包内置资源。
    """
    # 获取可执行文件所在的目录（打包后为 exe 所在目录；开发环境为脚本目录）
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    external = os.path.join(base_dir, folder_name)
    # 如果外部文件夹存在并且里面至少有一个文件，就使用它
    if os.path.exists(external) and os.listdir(external):
        return external
    else:
        # 否则使用打包内置资源（通过 resource_path）
        return resource_path(folder_name)

IMAGE_FOLDER = get_resource_folder('images')
MOUSE = get_resource_folder('mouse')
TAIL = get_resource_folder('tails')
AUX_FOLDER = 'auxiliary'


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        # 准备图片列表和当前索引
        try:
            valid_extensions = ('.png', '.jpg', '.jpeg', '.gif')
            image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(valid_extensions)]
            self.image_paths = sorted(
                [os.path.join(IMAGE_FOLDER, p) for p in image_files],
                key=lambda x: int(re.findall(r'\d+', x)[-1]) if re.findall(r'\d+', x) else 0
            )
        except Exception as e:
            print(f"读取图片失败: {e}")
            self.image_paths = []

        self.mouse_folder = MOUSE
        self.current_index = 0
        self.config_path = os.path.join(AUX_FOLDER, "config.json")
        self.pet_name = ""
        self.load_config()
        self.init_ui()

        # ---- 🌟 保留尾巴替身和计时器，但去掉动画 ----
        self.is_docked = False
        self.hide_timer = QTimer(self)
        self.hide_timer.setInterval(10000)          # 10秒
        self.hide_timer.timeout.connect(self.dock_to_side)   # 直接贴墙（无动画）
        self.hide_timer.start()

        # 创建尾巴替身窗口
        self.tail_widget = TailWidget(self)
        self.tail_widget.hide()

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

        # 图片标签
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

        # 设置逗猫棒鼠标指针
        teaser_files = glob.glob(os.path.join(self.mouse_folder, "*.png"))
        if teaser_files:
            teaser_path = teaser_files[0]
            if os.path.exists(teaser_path):
                teaser_pixmap = QPixmap(teaser_path)
                teaser_pixmap = teaser_pixmap.scaled(
                    32, 32,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                custom_cursor = QCursor(teaser_pixmap, 0, 0)
                self.setCursor(custom_cursor)
            else:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                print("⚠️ 未找到鼠标指针图片，已使用默认小手指针。")
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            print("⚠️ mouse文件夹为空，已使用默认小手指针。")

    def update_image(self):
        """智能加载：自动识别并显示静态图或GIF动图"""
        if not self.image_paths:
            return

        current_image = self.image_paths[self.current_index]

        # 清理之前的GIF
        if hasattr(self, 'movie') and self.movie:
            self.movie.stop()
            self.movie.deleteLater()
            self.movie = None

        if current_image.lower().endswith('.gif'):
            self.movie = QMovie(current_image)
            if not self.movie.isValid():
                print(f"❌ 警告：无法解析 GIF 文件: {current_image}")
                return

            target_width = 150
            self.movie.jumpToFrame(0)
            original_size = self.movie.currentImage().size()
            if original_size.width() > 0:
                target_height = int(target_width * original_size.height() / original_size.width())
                self.movie.setScaledSize(QSize(target_width, target_height))

            self.image_label.setMovie(self.movie)
            self.movie.start()
        else:
            pixmap = QPixmap(current_image)
            if pixmap.isNull():
                print(f"❌ 警告：无法解析静态图片: {current_image}")
                return

            pixmap = pixmap.scaledToWidth(150, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(pixmap)

        self.image_label.adjustSize()
        self.resize(self.image_label.size())

    def show_bubble(self, text=None):
        if hasattr(self, 'bubble') and self.bubble:
            self.bubble.close()
            self.bubble.deleteLater()

        messages = [
            f"我是{self.pet_name}，喵~",
            f"今天也要加油呀！",
            f"点{self.pet_name}干嘛？要抱抱吗？",
            f"别摸了，{self.pet_name}毛都要掉光了...",
            f"{self.pet_name}在盯着你写代码哦~"
        ]
        display_text = text if text else random.choice(messages)

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

        bubble_x = self.x() + (self.width() - self.bubble.width()) // 2
        bubble_y = self.y() - self.bubble.height() - 10
        self.bubble.move(bubble_x, bubble_y)
        self.bubble.show()
        QTimer.singleShot(3000, self.bubble.close)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(200, lambda: self.show_bubble(f"{self.pet_name} 来陪你啦！"))

    # ---------- 拖拽、点击等交互 ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            if self.image_paths:
                self.current_index = (self.current_index + 1) % len(self.image_paths)
                self.update_image()
            self.show_bubble()
            # 任何操作都重置发呆计时器
            self.hide_timer.start()

    def mouseMoveEvent(self, event):
        if not self._drag_pos.isNull() and event.buttons() == Qt.MouseButton.LeftButton:
            # 计算移动距离并更新位置
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

            # 让气泡跟着猫咪一起动
            if hasattr(self, 'bubble') and self.bubble.isVisible():
                bubble_x = self.x() + (self.width() - self.bubble.width()) // 2
                bubble_y = self.y() - self.bubble.height() - 10
                self.bubble.move(bubble_x, bubble_y)

            # # 🌟 关键修改：当小猫左边缘距离屏幕左边 ≤ 10 像素时，自动隐藏
            # if self.x() <= 10 and not self.is_docked:
            #     self.dock_to_side()  # 瞬间隐藏，显示尾巴
            #     self._drag_pos = QPoint()  # 结束拖拽状态

        # 拖动也算操作，重置发呆计时器
        self.hide_timer.start()

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

    # ---- 🌟 核心：瞬间贴墙 / 瞬间弹出 ----
    def dock_to_side(self):
        """立即隐藏主窗口，并在左侧显示尾巴"""
        if self.is_docked:
            return
        self.is_docked = True
        self.hide_timer.stop()

        # 记录当前 y 坐标（供弹出时使用）
        self.last_y = self.y()

        # 彻底隐藏主窗口
        self.hide()

        # 显示尾巴，贴在屏幕左边
        self.tail_widget.move(0, self.last_y)
        self.tail_widget.show()

    def undock_from_side(self):
        """鼠标碰到/点击尾巴后，立即弹出主窗口，隐藏尾巴"""
        if not self.is_docked:
            return
        self.is_docked = False

        self.tail_widget.hide()

        # 恢复主窗口到屏幕边缘，使用之前保存的 y 坐标
        self.move(0, self.last_y)
        self.setWindowOpacity(1.0)  # 确保不透明
        self.show()  # 重新显示
        self.raise_()  # 提到最上层
        self.update()  # 立即重绘

        self.hide_timer.start()
        self.show_bubble("捉到你啦~")

class TailWidget(QWidget):
    """显示在屏幕左侧边缘的尾巴替身"""

    def __init__(self, pet_parent):
        super().__init__()
        self.pet_parent = pet_parent

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(self)

        # self.label.setStyleSheet("background-color: rgba(255,0,0,30);")  # 调试用，可注释掉

        tail_files = glob.glob(os.path.join(TAIL, '*.png'))
        if tail_files:
            tail_path = tail_files[0]
            if os.path.exists(tail_path):
                pixmap = QPixmap(tail_path)
                # 缩放宽度与主体图片一致（150）
                scaled_pix = pixmap.scaledToWidth(60, Qt.TransformationMode.SmoothTransformation)
                self.label.setPixmap(scaled_pix)
                self.label.adjustSize()
                self.resize(self.label.size())
            else:
                self.label.setText("🐾")
                self.label.setStyleSheet("font-size: 30px;")
                self.label.adjustSize()
                self.resize(self.label.size())
        else:
            self.label.setText("🐾")
            self.label.setStyleSheet("font-size: 30px;")
            self.label.adjustSize()
            self.resize(self.label.size())

        # 加一点阴影让尾巴更有立体感
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(5)
        shadow.setXOffset(1)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.label.setGraphicsEffect(shadow)

    def enterEvent(self, event):
        super().enterEvent(event)
        if self.pet_parent.is_docked:
            self.pet_parent.undock_from_side()

    def mousePressEvent(self, event):
        """点击尾巴也能弹出猫咪（双重保障）"""
        super().mousePressEvent(event)
        if self.pet_parent.is_docked:
            self.pet_parent.undock_from_side()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())
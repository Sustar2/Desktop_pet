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
import random
import sys, os, re, json
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QMenu, QInputDialog
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtCore import Qt, QPoint, QTimer

IMAGE_FOLDER='images'
AUX_FOLDER='auxiliary'

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        # 1. 准备图片列表和当前索引
        self.image_paths = sorted(
            [os.path.join(IMAGE_FOLDER, path) for path in os.listdir(IMAGE_FOLDER)],
            # 提取路径中的所有数字，取最后那一组，转化为整数用于排序。如果没找到数字则默认排在前面(返回0)
            key=lambda x: int(re.findall(r'\d+', x)[-1]) if re.findall(r'\d+', x) else 0
        )
        self.current_index = 0  # 默认显示列表里的第 0 张（即 cat1.png）

        # 定义配置文件的路径
        self.config_path = os.path.join(AUX_FOLDER, "config.json")

        # 默认名字
        self.pet_name = ""

        # 尝试读取保存的名字
        self.load_config()


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

        # 加载初始图片并调整窗口大小
        self.update_image()

        # 初始化记录鼠标拖拽位置的变量
        self._drag_pos = QPoint()

        # --- 更新：计算并设置初始位置到屏幕 8/10 的位置 ---
        # 1. 获取屏幕的可用几何尺寸（自动避开任务栏）
        screen_geo = QApplication.primaryScreen().availableGeometry()

        # 2. 计算 8/10 的位置 (乘以 0.8)
        # 为了让猫咪的“中心点”而不是“左上角”对齐到 8/10 处，我们减去它自身宽高的一半
        x = int(screen_geo.width() * 0.8 - self.width() / 2)
        y = int(screen_geo.height() * 0.8 - self.height() / 2)

        # 3. 移动窗口到指定位置
        self.move(x, y)

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
        # 只有左键按下时，记录位置并切换图片
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.update_image()

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

    # --- 右键菜单栏 ---#
    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        context_menu.setStyleSheet("""
            QMenu { background-color: rgba(30, 30, 30, 200); color: white; border: 1px solid #FFB6C1; border-radius: 5px; }
            QMenu::item { padding: 5px 20px 5px 20px; }
            QMenu::item:selected { background-color: #FFB6C1; color: black; }
        """)

        # --- 新增：改名选项 ---
        rename_action = QAction("给宠物改名", self)
        rename_action.triggered.connect(self.change_name_dialog)
        context_menu.addAction(rename_action)

        # 添加分隔线（可选）
        context_menu.addSeparator()

        # 退出选项（保留之前的）
        quit_action = QAction("退出桌宠", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        context_menu.addAction(quit_action)

        context_menu.exec(event.globalPos())

    def change_name_dialog(self):
        """弹出输入框让用户修改名字"""
        # QInputDialog.getText 会返回用户输入的文本和是否点击了"确定"
        new_name, ok = QInputDialog.getText(self, "修改名字", "请输入宠物的名字：", text=self.pet_name)

        if ok and new_name.strip():  # 确保用户点了确定且没有只输入空格
            self.pet_name = new_name.strip()
            self.save_config()  # 保存到本地

    # --- pet 说话 --- #
    def showEvent(self, event):
        super().showEvent(event)
        # 窗口显示后，延迟 200 毫秒显示气泡（确保此时猫咪的坐标已经生成）
        QTimer.singleShot(200, self.show_startup_message)

    def show_startup_message(self):
        # 1. 准备你的启动语词库
        messages = [
            f"主人，我是{self.pet_name}，我来啦！ (ฅ´ω`ฅ)",
            f"{self.pet_name}今天也要元气满满哦！",
            f"喵喵喵~ {self.pet_name}等你好久了！",
            f"代码写累了就来摸摸{self.pet_name}吧~"
        ]
        text = random.choice(messages)

        # 2. 创建一个独立的对话气泡
        self.bubble = QLabel(text)
        self.bubble.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.bubble.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 3. 给气泡设置可爱的样式（半透明白底，粉色圆角边框）
        # 给气泡设置深色背景+白色字体的样式
        self.bubble.setStyleSheet("""
                    QLabel {
                        background-color: rgba(30, 30, 30, 200); /* 半透明的深灰色背景 */
                        border: 2px solid #FFB6C1;               /* 依然保留粉色边框，你可以改为 #FFFFFF 变成纯白边框 */
                        border-radius: 10px;                     /* 圆角 */
                        padding: 8px 12px;                       /* 内边距 */
                        font-size: 14px;                         /* 字体大小 */
                        color: white;                            /* 字体设为纯白色 */
                        font-weight: bold;                       /* 字体加粗 */
                    }
                """)
        self.bubble.adjustSize()

        # 4. 计算气泡位置，让它出现在猫咪的正上方稍微偏中间的位置
        bubble_x = self.x() + (self.width() - self.bubble.width()) // 2
        bubble_y = self.y() - self.bubble.height() - 10
        self.bubble.move(bubble_x, bubble_y)

        self.bubble.show()

        # 5. 核心：设置定时器，3000毫秒（即3秒）后自动关闭并销毁这个气泡
        QTimer.singleShot(3000, self.bubble.close)

    # --- 宠物名字 --- #
    def load_config(self):
        """直接检查 config.json，没有就原地生成一个"""
        # 只需要判断文件存不存在
        if not os.path.exists(self.config_path):
            # 不存在的话，直接调用保存方法，它会自动生成并写入默认数据
            self.save_config()
        else:
            # 存在的话，正常读取
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.pet_name = data.get("pet_name", "小猫咪")
            except Exception as e:
                print(f"读取配置失败，可能文件格式损坏，重新生成默认配置: {e}")
                self.save_config()

    def save_config(self):
        """负责把数据写入文件，并进行梳妆打扮"""
        # 准备好默认的数据
        data_to_save = {
            "pet_name": self.pet_name
        }

        # 既然你确定 auxiliary 文件夹在，那就毫不犹豫地直接创建/覆盖文件！
        with open(self.config_path, 'w', encoding='utf-8') as f:
            # indent=4 就是你要的“梳妆打扮”，它会让 JSON 自动换行并缩进4个空格
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())
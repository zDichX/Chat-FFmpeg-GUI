from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QButtonGroup, QDesktopWidget, QFileDialog, QErrorMessage
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QTimer, QPoint, QThread

import shutil
import math
import sys
import os
import subprocess

class FFmpegWorker(QThread):
    def __init__(self, command):
        super().__init__()
        self.command = command
    def check_ffmpeg(self):
        return shutil.which("ffmpeg") is not None
    def run(self):
        try:
            if not self.check_ffmpeg():
                current_directory = os.getcwd()
                ffmpeg_files = [f for f in os.listdir(current_directory) if f.startswith('ffmpeg')]
                if ffmpeg_files:
                    ffmpeg_file = ffmpeg_files[0]
                    file_path = os.path.join(current_directory, ffmpeg_file, 'bin', 'ffmpeg.exe')
                    self.command = self.command.replace("ffmpeg -i", f"{file_path} -i")
            subprocess.run(self.command, shell=True)
        finally:
            self.finished.emit()

class FFmpegWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.initUI()
        self.apply_styles()
        self.delayed_animation_start()

    def initUI(self):
        self.setWindowTitle("FFmpeg GUI Converter")
        self.setFixedSize(500, 309)

        # 布局
        self.layout = QVBoxLayout()

        # 文本1
        self.file_label = QLabel("Enter or Drag:")
        self.layout.addWidget(self.file_label)
        
        # 路径 + 选择按钮容器
        self.path_layout = QHBoxLayout()

        # 路径
        self.path_input = QLineEdit()
        self.path_input.textChanged.connect(self.generate_command)
        self.path_layout.addWidget(self.path_input)

        # 选择文件按钮
        self.select_file_button = QPushButton("Choose...")
        self.select_file_button.clicked.connect(self.open_file_dialog)
        self.path_layout.addWidget(self.select_file_button)

        # 添加到主布局
        self.layout.addLayout(self.path_layout)

        # 文本2
        self.format_label = QLabel("Output Format:")
        self.layout.addWidget(self.format_label)

        # 格式按钮组
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(5)
        self.buttonGroup = QButtonGroup(self)
        formats = ["MP4", "MKV", "AVI", "MP3", "WAV", "FLAC"]
        for format in formats:
            button = QPushButton(format)
            button.setCheckable(True)
            self.buttonGroup.addButton(button)
            self.button_layout.addWidget(button)
        self.buttonGroup.buttonClicked.connect(self.generate_command)
        self.layout.addLayout(self.button_layout)

        self.command_line = QLineEdit()
        self.command_line.setPlaceholderText('(￣﹃￣)')
        self.command_line.setReadOnly(True)
        self.layout.addWidget(self.command_line)

        # self.generate_button = QPushButton("Preview")
        # self.generate_button.clicked.connect(self.generate_command)
        # self.layout.addWidget(self.generate_button)

        # 生成按钮
        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self.execute_command)
        self.layout.addWidget(self.execute_button)

        # 应用窗口
        self.setLayout(self.layout)

    # QSS样式
    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif; /* 设置全局字体为 Roboto */
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #e0c3fc, stop: 1 #8ec5fc
                );
                color: #000000; 
                font-size: 20px;
                border-radius: 20px;
                
            }
            QLabel{
                background: none;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.4); /* 输入框背景 */
                border: 2px solid #ffffff; /* 输入框边框颜色 */
                padding-left: 15px; /* 内边距 */
                padding-right: 10px;
                padding-top: 5px;
                padding-bottom: 5px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.4);/* 按钮背景颜色 */
                border: none;
                padding: 10px;
            }    
            QPushButton:hover {
                background-color: rgba(150, 150, 150, 0.4); /* 鼠标悬停时的颜色 */
            }
            QPushButton:checked {
                background-color: white;  /* 选中状态颜色 */
            }
        """)

    def start_animation(self):
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(1000)
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(QPoint(self.pos().x(), self.pos().y() + 100))
        self.pos_animation.setEasingCurve(QEasingCurve.OutBounce)
        self.pos_animation.start()

    def move_to_center(self):
        self.screen_center = self.get_screen_center()
        self.window_center = QPoint(self.width() // 2, self.height() // 2)
        self.mov_animation = QPropertyAnimation(self, b"pos")
        self.mov_animation.setDuration(600)
        self.mov_animation.setStartValue(self.pos())
        self.mov_animation.setEndValue(QPoint(self.screen_center.x() - self.window_center.x(), self.screen_center.y() - self.window_center.y()))
        self.mov_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.mov_animation.finished.connect(self.mov_animation_finished)
        self.mov_animation.start()

    def mov_animation_finished(self):
        self.processing_animation()

    def processing_animation(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(16)  # 60 FPS

        self.screen_center = self.get_screen_center()
        self.window_center = QPoint(self.width() // 2, self.height() // 2)
        self.t = 0
        self.step = 0

    def get_screen_center(self):
        screen = QDesktopWidget().screenGeometry()
        return QPoint(screen.width() // 2, screen.height() // 2)

    def update_position(self):
        radius = 200
        self.t += self.step
        if self.step <= 0.6:
            self.step += 0.0002
        x = int(self.screen_center.x() + radius * math.sin(self.t) - self.window_center.x())
        y = int(self.screen_center.y() + radius * math.sin(self.t) * math.cos(self.t)- self.window_center.y())
        self.move(x, y)

    def delayed_animation_start(self):
        delay = 0
        QTimer.singleShot(delay, self.start_animation)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isfile(path) or os.path.isdir(path):
                self.path_input.setText(path)

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "", "", "all files (*);;vedio (*.mp4 *.mkv *.avi);;audio (*.mp3 *.wav *.flac)", options=options)
        if file_name:
            self.path_input.setText(file_name)

    def generate_command(self):
        path = self.path_input.text()
        if os.path.isfile(path) and self.buttonGroup.checkedButton():
            self.command_line.setReadOnly(False)
            output_format = self.buttonGroup.checkedButton().text().lower()
            output_path = f"{path.rsplit('.', 1)[0]}.{output_format}"
            command = f"ffmpeg -i \"{path}\" \"{output_path}\""
            self.command_line.setText(command)
        elif os.path.isdir(path):
            self.command_line.setReadOnly(False)
            self.command_line.setText("")
            self.command_line.setPlaceholderText('Parameters (e.g. -b:v 1M -b:a 128k)')
        else:
            self.command_line.setReadOnly(True)
            self.command_line.setText("")
            self.command_line.setPlaceholderText("qwq?")


    def execute_command(self):
        if self.buttonGroup.checkedButton():
            self.execute_button.setDisabled(True)
            self.execute_button.setText("Executing...")
            path = self.path_input.text()
            output_format = self.buttonGroup.checkedButton().text().lower()
        else:
            print("为什么不选格式？？\nWhy don't you choose the format??")
            return
        
        if os.path.isfile(path):
            output_path = os.path.splitext(path)[0] + '.' + output_format
            command = self.command_line.text() or f"ffmpeg -i \"{path}\" \"{output_path}\""
            self.run_command_in_thread(command)
        elif os.path.isdir(path):
            output_dir = os.path.join(path, "converted_files")
            os.makedirs(output_dir, exist_ok=True)
            commands = []
            for file_name in os.listdir(path):
                file_path = os.path.join(path, file_name)
                if os.path.isfile(file_path):
                    output_path = os.path.join(output_dir, os.path.splitext(file_name)[0] + '.' + output_format)
                    command = f"ffmpeg -i \"{file_path}\" {self.command_line.text()} \"{output_path}\""
                    commands.append(command)
            combined_command = ' && '.join(commands)
            self.run_command_in_thread(combined_command)
        else:
            print("Invalid input path.")

    def run_command_in_thread(self, command):
        self.worker = FFmpegWorker(command)
        self.worker.finished.connect(self.close)
        self.worker.start()

        self.move_to_center()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = FFmpegWidget()
    demo.show()
    sys.exit(app.exec_())
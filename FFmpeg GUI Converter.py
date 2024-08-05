from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QButtonGroup, QFileDialog
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer, QPoint, QThread, Qt, pyqtSignal

import re, os, sys, math, subprocess

class FFmpegWorker(QThread):
    progress_updated = pyqtSignal(float)  # 定义进度更新信号

    def __init__(self, input_path, output_path, inp_params, out_params):
        super().__init__()
        if isinstance(input_path, list):
            self.input_path = input_path
            self.output_path = output_path
        else:
            self.input_path = [input_path]
            self.output_path = [output_path]

        self.inp_params = inp_params + " "
        self.out_params = out_params + " "
        self.processes = []  # 存储子进程的列表

    def get_duration(self, file_path):
        command = ['ffmpeg', '-i', file_path]
        result = subprocess.run(command, stderr=subprocess.PIPE, text=True, errors='ignore')
        duration_pattern = re.compile(r'Duration: (\d+):(\d+):(\d+.\d+)')
        match = duration_pattern.search(result.stderr)
        if match:
            h, m, s = map(float, match.groups())
            return h * 3600 + m * 60 + s
        return None
    
    # 检测并安装ffmpeg
    def detect_ffmpeg(self):
        try:
            subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            try:
                subprocess.run(['winget', 'install', 'FFmpeg (Essentials Build)'], check=True)
            except:
                sys.exit(1)

    def run(self):
        self.detect_ffmpeg()
        try:
            total_duration = 0
            accumulated_elapsed_seconds = 0

            # 计算所有文件的总时长
            for value in self.input_path:
                duration = self.get_duration(value)
                if duration is not None:
                    total_duration += duration

            # 遍历每个文件进行转换
            for index, value in enumerate(self.input_path):
                command = f"ffmpeg -y {self.inp_params}-i \"{value}\" {self.out_params}\"{self.output_path[index]}\""
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW)
                self.processes.append(process)
                progress_pattern = re.compile(r'time=(\d+):(\d+):(\d+.\d+)')
                last_elapsed_seconds = 0  # 记录当前文件上一次已处理的秒数
                for line in process.stderr:
                    line = line.strip()
                    match = progress_pattern.search(line)
                    if match:
                        h, m, s = map(float, match.groups())
                        elapsed_seconds = h * 3600 + m * 60 + s
                        
                        # 累加当前文件的进度差值
                        accumulated_elapsed_seconds += max(0, elapsed_seconds - last_elapsed_seconds)
                        last_elapsed_seconds = elapsed_seconds
                        
                        # 计算并发射综合进度
                        overall_progress = min(accumulated_elapsed_seconds / total_duration, 1.0)
                        self.progress_updated.emit(overall_progress)
                        
                process.wait()
        finally:
            pass
    def terminate_processes(self):
        for process in self.processes:
            if process.poll() is None:  # 检查进程是否仍在运行
                process.terminate()
                process.wait()


class FFmpegWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.worker = None  # 初始化 worker 变量
        self.initUI()
        self.apply_styles()
        self.delayed_animation_start()
        

    def initUI(self):
        self.setWindowTitle("FFmpeg GUI Converter")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(324, 200)

        # 布局
        self.layout = QVBoxLayout()

        # 文本1
        self.file_label = QLabel("Enter or Drag:")
        self.layout.addWidget(self.file_label)
        
        # 路径 + 选择按钮容器
        self.path_layout = QHBoxLayout()

        # 路径
        self.path_input = QLineEdit()
        # self.path_input.textChanged.connect(self.generate_command)
        self.path_input.setPlaceholderText("File or directory")
        self.path_layout.addWidget(self.path_input)

        # 选择文件按钮
        self.select_file_button = QPushButton("Choose...")
        self.select_file_button.clicked.connect(self.open_file_dialog)
        self.path_layout.addWidget(self.select_file_button)

        # 添加到主布局
        self.layout.addLayout(self.path_layout)

        # 文本2
        self.format_label = QLabel("Parameters:")
        self.layout.addWidget(self.format_label)

        # self.command_line = QLineEdit()
        # self.command_line.setPlaceholderText('(￣﹃￣)')
        # self.command_line.setReadOnly(True)
        # self.layout.addWidget(self.command_line)

        # 参数
        self.parameters_layout = QHBoxLayout()
        self.inp_params_line = QLineEdit()
        self.inp_params_line.setPlaceholderText('input')
        self.parameters_layout.addWidget(self.inp_params_line)

        self.out_params_line = QLineEdit()
        self.out_params_line.setPlaceholderText('output')
        self.parameters_layout.addWidget(self.out_params_line)

        # self.vfil_params_line = QLineEdit()
        # self.vfil_params_line.setPlaceholderText('vfilter')
        # self.parameters_layout.addWidget(self.vfil_params_line, 1, 0)

        # self.afil_params_line = QLineEdit()
        # self.afil_params_line.setPlaceholderText('afilter')
        # self.parameters_layout.addWidget(self.afil_params_line, 1, 1)

        self.layout.addLayout(self.parameters_layout)

        # 格式按钮组
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(5)
        self.buttonGroup = QButtonGroup(self)
        formats = ["MP4", "AVI", "MP3", "WAV", "FLAC"]
        for format in formats:
            button = QPushButton(format)
            button.setCheckable(True)
            button.setMinimumWidth(45)
            self.buttonGroup.addButton(button)
            self.button_layout.addWidget(button)
        self.buttonGroup.buttonClicked.connect(lambda: self.exclusive_detect("choosing"))
        self.custom_format = QLineEdit()
        self.button_layout.addWidget(self.custom_format)
        self.custom_format.textChanged.connect(lambda: self.exclusive_detect("typing"))
        self.layout.addLayout(self.button_layout)

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
                font-size: 13px;
                border-radius: 13px;
                
            }
            QLabel{
                background: none;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.4); /* 输入框背景 */
                border: 2px solid #ffffff; /* 输入框边框颜色 */
                padding-left: 10px; /* 内边距 */
                padding-right: 10px;
                padding-top: 3px;
                padding-bottom: 3px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.4);/* 按钮背景颜色 */
                border: none;
                padding: 6px;
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
        self.pos_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        self.pos_animation.start()

    def move_to_center(self):
        self.screen_center = self.get_screen_center()
        self.window_center = QPoint(self.width() // 2, self.height() // 2)
        self.mov_animation = QPropertyAnimation(self, b"pos")
        self.mov_animation.setDuration(600)
        self.mov_animation.setStartValue(self.pos())
        self.mov_animation.setEndValue(QPoint(self.screen_center.x() - self.window_center.x(), self.screen_center.y() - self.window_center.y() - 100))
        self.mov_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.mov_animation.finished.connect(self.processing_animation)
        self.mov_animation.start()

    def processing_animation(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(16)  # 60 FPS

        self.screen_center = self.get_screen_center()
        self.window_center = QPoint(self.width() // 2, self.height() // 2)
        self.t = 0
        self.step = 0

    def get_screen_center(self):
        screen = QApplication.primaryScreen().geometry()
        return QPoint(screen.width() // 2, screen.height() // 2)

    def update_position(self):
        radius = 100
        if self.step >= 0:
            self.t += self.step
            if self.t <= 10000:
                self.step += (0.5 - self.progress) / 300
        else:
            self.timer.stop()
            return
        
        angle = self.t - math.pi / 2
        x = int(self.screen_center.x() + radius * math.cos(angle) - self.window_center.x())
        y = int(self.screen_center.y() + radius * math.sin(angle) - self.window_center.y())
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
        file_name, _ = QFileDialog.getOpenFileName(self, "", "", "all files (*);;video (*.mp4 *.mkv *.avi);;audio (*.mp3 *.wav *.flac)", options=options)
        if file_name:
            self.path_input.setText(file_name)

    def exclusive_detect(self, state):
        if state == "typing": 
            selected_button = self.buttonGroup.checkedButton()
            if selected_button:
                self.buttonGroup.setExclusive(False)
                selected_button.setChecked(False)
                self.buttonGroup.setExclusive(True)
        elif state == "choosing":
            self.custom_format.setText("")


    def execute_command(self):

        path = self.path_input.text()
        if self.buttonGroup.checkedButton():
            output_format = self.buttonGroup.checkedButton().text().lower()
        elif self.custom_format.text() and self.custom_format.text() != "":
            output_format = self.custom_format.text()
        else:
            # print("Please choose a format")
            self.execute_button.setText("Please choose a format")
            return
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        self.execute_button.setDisabled(True)
        self.execute_button.setText("Executing...")
        self.progress = 0
        if os.path.isfile(path):
            
            # command = self.command_line.text() or f"ffmpeg -i \"{path}\" \"{output_path}\""
            self.run_command_in_thread(path, os.path.splitext(path)[0] + '_converted.' + output_format, self.inp_params_line.text(), self.out_params_line.text())
            
        elif os.path.isdir(path):
            output_dir = os.path.join(path, "converted_files")
            os.makedirs(output_dir, exist_ok=True)
            # commands = []
            input_path = []
            output_path = []
            for file_name in os.listdir(path):
                file_path = os.path.join(path, file_name)
                if os.path.isfile(file_path):
                    input_path.append(file_path)
                    output_path.append(os.path.join(output_dir, os.path.splitext(file_name)[0] + '.' + output_format))
                    # command = f"ffmpeg -i \"{file_path}\" {self.command_line.text()} \"{output_path}\""
                    # commands.append(command)
            # combined_command = ' && '.join(commands)
            self.run_command_in_thread(input_path, output_path, self.inp_params_line.text(), self.out_params_line.text())
        else:
            # print("Invalid input path.")
            self.execute_button.setDisabled(False)
            self.execute_button.setText("Invalid input path")
            return

    def run_command_in_thread(self, input_path, output_path, inp_params, out_params):
        self.worker = FFmpegWorker(input_path, output_path, inp_params, out_params)
        self.worker.progress_updated.connect(self.update_progress)  # 连接进度更新信号
        self.worker.finished.connect(self.conversion_finished)
        self.worker.start()
        if not os.path.isfile('no_animation_plz.txt'):
            self.move_to_center()

    def update_progress(self, progress):
        self.execute_button.setText(f"{progress * 100:.2f}%")
        self.progress = progress
        
    def conversion_finished(self):
        self.execute_button.setDisabled(False)
        self.execute_button.setText("Finished")

    def closeEvent(self, event):
        if self.worker is not None:
            self.worker.terminate_processes()
        event.accept()  # 确保关闭事件继续进行
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = FFmpegWidget()
    demo.show()
    sys.exit(app.exec())
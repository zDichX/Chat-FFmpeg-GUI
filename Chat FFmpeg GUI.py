from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QButtonGroup, QFileDialog
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer, QPoint, QThread, Qt, pyqtSignal
from PyQt6.QtGui import QIcon

import re, os, sys, math, json, requests, subprocess

class FFmpegWorker(QThread):
    progress_updated = pyqtSignal(float)  # 定义进度更新信号

    def __init__(self, file_info, ai_commands):
        super().__init__()
        self.processes = []  # 存储子进程的列表
        self.input_path = file_info['input_path']
        self.output_path = file_info['output_path']
        self.ai_commands = ai_commands
        # self.inp_params = inp_params + " "
        # self.out_params = out_params + " "
        
    def get_duration(self, ffmpar, file_path):
        command = [ffmpar, '-i', file_path]
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
            return 'ffmpeg'
        except:
            try:
                current_directory = os.getcwd()
                ffmpeg_path = [file for file in os.listdir(current_directory) if file.startswith('ffmpeg')]
                if ffmpeg_path[0]:
                    return os.path.join(current_directory, ffmpeg_path[0], 'bin', 'ffmpeg.exe')
                else:
                    subprocess.run(['winget', 'install', 'FFmpeg (Essentials Build)'], check=True)
                    subprocess.call([sys.executable] + sys.argv)
                    sys.exit(0)
            except:
                sys.exit(1)

    def run(self):
        self.ffmpeg_par = self.detect_ffmpeg()
        try:
            total_duration = 0
            accumulated_elapsed_seconds = 0

            # 计算所有文件的总时长
            for value in self.input_path:
                duration = self.get_duration(self.ffmpeg_par, value)
                if duration is not None:
                    total_duration += duration
                    

            # 遍历每个文件进行转换
            for index, value in enumerate(self.input_path):
                if self.ai_commands:
                    command = self.ai_commands[index]
                else:
                    # command = f"{self.ffmpeg_par} -y {self.inp_params}-i \"{value}\" {self.out_params}\"{self.output_path[index]}\""
                    command = f"{self.ffmpeg_par} -y -i \"{value}\" \"{self.output_path[index]}\""

                print(f'正在执行：{command}')
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
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)
        finally:
            self.terminate_processes()
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
        self.setWindowTitle("Chat FFmpeg GUI")
        icon_path = self.get_icon()
        self.setWindowIcon(QIcon(icon_path))
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

        # 转换为
        # self.output_layout = QHBoxLayout()

        # self.output_text = QLabel("Convert to: ")
        # self.output_layout.addWidget(self.output_text)

        # self.output_line = QLineEdit()
        # self.output_line.setPlaceholderText("File name will be ignore")
        # self.output_layout.addWidget(self.output_line)
        # self.layout.addLayout(self.output_layout)



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
        self.custom_format.setPlaceholderText('or...')
        self.button_layout.addWidget(self.custom_format)
        self.custom_format.textChanged.connect(lambda: self.exclusive_detect("typing"))
        self.layout.addLayout(self.button_layout)

        # self.command_line = QLineEdit()
        # self.command_line.setPlaceholderText('(￣﹃￣)')
        # self.command_line.setReadOnly(True)
        # self.layout.addWidget(self.command_line)

        # 参数
        # self.parameters_layout = QHBoxLayout()

        # self.inp_params_line = QLineEdit()
        # self.inp_params_line.setPlaceholderText('Input Parameters')
        # self.parameters_layout.addWidget(self.inp_params_line)

        # self.out_params_line = QLineEdit()
        # self.out_params_line.setPlaceholderText('Output Parameters')
        # self.parameters_layout.addWidget(self.out_params_line)

        # self.inp_anim = QPropertyAnimation(self.inp_params_line, b"windowOpacity")
        # self.inp_anim.setDuration(500)
        # self.inp_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        # self.inp_anim.setStartValue(1.0)
        # self.inp_anim.setEndValue(0.0)        

        # self.layout.addLayout(self.parameters_layout)
        
        # 生成按钮
        self.generate_layout = QHBoxLayout()
        self.ai_params_line = QLineEdit()
        self.ai_params_line.setPlaceholderText('(￣﹃￣)')
        self.generate_layout.addWidget(self.ai_params_line)

        self.generate_button = QPushButton('Generate')
        self.generate_button.clicked.connect(lambda: self.AiGenerate(self.ai_params_line.text()))
        self.generate_layout.addWidget(self.generate_button)

        self.layout.addLayout(self.generate_layout)

        # 生成的命令
        self.command_line = QLabel('( •̀ ω •́ )✧Preview here...')
        self.command_line.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.layout.addWidget(self.command_line)

        # 执行按钮
        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self.execute_command)
        self.layout.addWidget(self.execute_button)

        # 应用窗口
        self.setLayout(self.layout)

    # QSS样式
    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
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
                padding-left: 4px;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.4);
                border: 2px solid #ffffff;
                padding-left: 10px;
                padding-right: 10px;
                padding-top: 3px;
                padding-bottom: 3px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.4);
                border: none;
                padding: 6px;
            }    
            QPushButton:hover {
                background-color: rgba(150, 150, 150, 0.4);
            }
            QPushButton:checked {
                background-color: white;
            }
        """)

    # 获取图标
    def get_icon(self):
        if hasattr(sys, '_MEIPASS'):
            # 运行时目录
            base_path = sys._MEIPASS
        else:
            # 开发时目录
            base_path = os.path.abspath(".")
        icon_path = os.path.join(base_path, "icon.ico")
        return icon_path
    
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
        file_dialog = QFileDialog()
        options = file_dialog.options()
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


    def AiGenerate(self, text):
        print('AI接收到的文本：' + text)
        file_info = self.get_file_info()
        if isinstance(file_info, dict):
            with open('config.json', 'r') as file:
                ai_config = json.load(file)["ai_config"]

            url = ai_config["url"] + "/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {ai_config['api_key']}",
                "Content-Type": "application/json"
            }

            data = {
            'model': ai_config["model"],
            'messages': [
                {"role": "system", "content": f"Generate an ffmpeg command based on the following instructions. Assume the input file is input{file_info['input_format'][0]} and the output file is output{file_info['output_format']}. Please wrap the generated command in a markdown code block."},
                {"role": "user", "content": text}
            ],
            'temperature': ai_config["temperature"]
            }

            response = requests.post(url, headers=headers, json=data)
            response_json = response.json()

            AiText = response_json['choices'][0]['message']['content']


            match1 = re.findall(r'```[\w]*\n(.*?)```', AiText, re.DOTALL)
            match2 = re.search(r'ffmpeg .*', match1[0])
            print(f'GPT的输出：{match2.group()}')
            return self.undate_preview(match2.group())
        else:
            self.ai_params_line.setPlaceholderText(file_info)

    def undate_preview(self, command):
        self.command_line.setText(command)

    def get_file_info(self):
        path = self.path_input.text()

        if self.buttonGroup.checkedButton():
            output_format = self.buttonGroup.checkedButton().text().lower()
        elif self.custom_format.text() and self.custom_format.text() != "":
            output_format = self.custom_format.text().lower()
        else:
            # self.execute_button.setText("Please choose a format")
            return 'unknown_format'
        if os.path.isfile(path):
            file_info = {
                'input_format': [os.path.splitext(path)[1]],
                'output_format': '.' + output_format,
                'input_path': [path],
                'output_path': [os.path.splitext(path)[0] + '_converted.' + output_format]
            }
        elif os.path.isdir(path):
            input_format = []
            input_path = []
            output_path = []
            output_dir = os.path.join(path, "converted_files")
            os.makedirs(output_dir, exist_ok=True)
            for file_name in os.listdir(path):
                file_path = os.path.join(path, file_name)
                if os.path.isfile(file_path):
                    input_format.append(os.path.splitext(file_name)[1].lower())
                    input_path.append(file_path)
                    output_path.append(os.path.join(output_dir, os.path.splitext(file_name)[0] + '.' + output_format))
            file_info = {
                'input_format': input_format,
                'output_format': '.' + output_format,
                'input_path': input_path,
                'output_path': output_path
            }
        else:
            # self.execute_button.setDisabled(False)
            # self.execute_button.setText("Invalid input path")
            return 'invalid_input_path'
        return file_info
        
    def execute_command(self):
        file_info = self.get_file_info()
        if isinstance(file_info, dict):
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.show()
            self.execute_button.setDisabled(True)
            self.execute_button.setText("Executing...")
            self.progress = 0

            if self.command_line.text().startswith('ffmpeg '):
                commands = []
                ai_cmd = self.command_line.text()
                for index, value in enumerate(file_info['input_path']):
                    overflow = ai_cmd.replace('ffmpeg ', 'ffmpeg -y ')
                    rpInput = overflow.replace(f'input{file_info['input_format'][index]}', f'"{value}"')
                    rpOutput = rpInput.replace(f'output{file_info['output_format']}', f'"{file_info['output_path'][index]}"')
                    commands.append(rpOutput)
            else:
                commands = None

            print(f'即将发送 - 文件属性：{file_info}, 命令：{commands}')
            # self.run_command_in_thread(file_info['input_path'], file_info['output_path'], self.inp_params_line.text(), self.out_params_line.text())
            self.run_command_in_thread(file_info, commands)
            
        else:
            self.command_line.setText(f'━━Σ(ﾟдﾟ;). {file_info}...')
        
    def run_command_in_thread(self, file_info, commands):
        # print(f"input_path:{input_path}, output_path:{output_path}, inp_params:{inp_params}, out_params:{out_params}")
        self.worker = FFmpegWorker(file_info, commands)
        self.worker.progress_updated.connect(self.update_progress)  # 连接进度更新信号
        self.worker.finished.connect(self.conversion_finished)
        self.worker.start()
        with open('config.json', 'r') as file:
            if json.load(file)["animation"]:
                self.move_to_center()

    def update_progress(self, progress):
        self.execute_button.setText(f"{progress * 100:.2f}%")
        num_blocks = int(progress * 30)
        progress_bar = '█' * num_blocks + '░' * (30 - num_blocks)
        self.command_line.setText(progress_bar)

        self.progress = progress
    
    def conversion_finished(self):
        self.execute_button.setDisabled(False)
        self.execute_button.setText("Execute")
        file_info = self.get_file_info()
        if file_info['input_path'][0] and os.path.isfile(file_info['input_path'][0]):
            self.command_line.setText("Finished!")
        else:
            self.command_line.setText("Error...")

    def closeEvent(self, event):
        if self.worker is not None:
            self.worker.terminate_processes()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = FFmpegWidget()
    demo.show()
    sys.exit(app.exec())
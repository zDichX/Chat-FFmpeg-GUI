from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QButtonGroup, QFileDialog, QGraphicsOpacityEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from components.FFmpegWorker import FFmpegWorker
from components.AnimationManager import AnimationManager
import re, os, sys, json, requests


class FFmpegWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.worker = None  # 初始化 worker 变量
        self.anim = AnimationManager(self)
        self.initUI()
        self.apply_styles()
        self.anim.delayed_animation_start()

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

        # 生成按钮
        self.generate_layout = QHBoxLayout()
        self.ai_params_line = QLineEdit()
        self.ai_params_line.setPlaceholderText('How can I assist you today?')
        self.generate_layout.addWidget(self.ai_params_line)

        self.generate_button = QPushButton('Generate')
        self.generate_button.clicked.connect(lambda: self.handle_generation(self.ai_params_line.text()))
        self.generate_layout.addWidget(self.generate_button)

        self.layout.addLayout(self.generate_layout)

        # 生成的命令
        self.command_line = QLabel('( •̀ ω •́ )✧Preview here...')
        self.command_line.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.layout.addWidget(self.command_line)

        # 执行按钮
        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self.execute_command)
        
        # self.execute_button.clicked.connect(self.click_animation)
        self.layout.addWidget(self.execute_button)

        # 应用窗口
        self.setLayout(self.layout)

    # QSS样式
    def apply_styles(self):
        qss_content = open(os.path.join(os.getcwd(), 'style.qss')).read()
        self.setStyleSheet(qss_content)

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
        clicked_button = self.buttonGroup.checkedButton()
        if clicked_button:
            # 恢复所有按钮的透明度
            for button in self.buttonGroup.buttons():
                opacity_effect = QGraphicsOpacityEffect(button)
                button.setGraphicsEffect(opacity_effect)
                opacity_effect.setOpacity(1.0)

            # 为点击的按钮应用动画
            self.anim.click_animation(clicked_button)

        if state == "typing": 
            selected_button = self.buttonGroup.checkedButton()
            if selected_button:
                self.buttonGroup.setExclusive(False)
                selected_button.setChecked(False)
                self.buttonGroup.setExclusive(True)
        elif state == "choosing":
            self.custom_format.setText("")


    def handle_generation(self, text):
        try:
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
                    {"role": "system", "content": f"Generate an ffmpeg command based on the following instructions. Assume the input file is input{file_info['input_format'][0]} and the output file is output{file_info['output_format']}. Do not add any parameters that were not requested. Please wrap the generated command in a markdown code block."},
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
                self.command_line.setText(file_info)
        except Exception as e:
            print(f"error: {str(e)}")
            if str(e) == "'choices'" or 'Connection aborted' in str(e):
                error_info = '`config.json` seems to be incorrect.'
            else:
                error_info = f"error: {str(e)}"
            self.command_line.setText(error_info)
            return

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
            return 'Unknown format'
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
            return 'Invalid input path'
        return file_info
        
    def execute_command(self):
        file_info = self.get_file_info()
        if isinstance(file_info, dict):
            self.setWindowFlags(self.windowFlags() & Qt.WindowType.WindowStaysOnBottomHint)
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
        # with open('config.json', 'r') as file:
        #     if json.load(file)["animation"]:
        #         self.anim.move_to_center()

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
            self.worker.terminate_processes()  # 确保关闭 FFmpeg 进程
            self.worker.quit()  # 停止工作线程
            self.worker.wait()  # 等待线程结束
        event.accept()  # 接受关闭事件

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = FFmpegWidget()
    demo.show()
    sys.exit(app.exec())
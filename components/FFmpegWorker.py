from PySide6.QtCore import QThread, Signal

import re, os, sys, subprocess

class FFmpegWorker(QThread):
    progress_updated = Signal(float)  # 定义进度更新信号

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

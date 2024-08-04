# FFmpeg GUI Converter

不太实用的ffmpeg gui，能实现基本的格式转换
<br><br>
![image](https://github.com/user-attachments/assets/65b4883c-c227-4119-8872-695ea72b7bdb)


## 特点

- 能处理大部分简单的FFmpeg任务
- 可以处理文件目录
- 可添加额外参数
- 进度条(简陋的)
- 多余的动画
- 传奇依托白话菜比代码

## 安装

### 安装FFmpeg（非常重要）

如果你还没有安装FFmpeg，可以通过以下两种方式进行安装：

- 使用 `winget` 安装：
  ```shell
  winget install "FFmpeg (Essentials Build)"
  ```

### 方法一：下载预编译的可执行文件

1. 访问 [Releases 页面](https://github.com/zDichX/FFmpeg-GUI-Converter/releases) 
2. 下载最新版本的 `.exe` 程序
3. 运行程序

### 方法二：Git Clone

1. 不用教

## 用法

1. 拖拽文件到窗口或选择文件
2. 填写参数（非必须） 
3. 选择目标格式
4. 点击 **Execute** 按钮
5. 等待转换完成

### 参数示例

#### input
```shell
-ss 00:00:10 -t 00:01:00
```
#### output
```shell
-vf "scale=1280:720,crop=640:480,transpose=1" -af "atrim=start=5,volume=2" -c:v libx264 -crf 23
```
具体解释如下：
- `-ss 00:00:10`：从视频的第10秒开始处理。
- `-t 00:01:00`：持续处理1分钟。
- `-i input.mp4`：指定输入文件 `input.mp4`。
- `-vf "scale=1280:720,crop=640:480,transpose=1"`：应用视频过滤器（video filter）。
  - `scale=1280:720`：将视频缩放到1280x720像素。
  - `crop=640:480`：从缩放后的视频中裁剪出640x480像素的区域。
  - `transpose=1`：将视频顺时针旋转90度。
- `-af "atrim=start=5,volume=2"`：应用音频过滤器（audio filter）。
  - `atrim=start=5`：从音频的第5秒开始截取。
  - `volume=2`：将音量提高2倍。
- `-c:v libx264`：指定视频编码器为 `libx264`。
- `-crf 23`：指定恒定速率因子（CRF）为23，控制视频质量。

更多请参阅：[FFmpeg官方文档](https://ffmpeg.org/ffmpeg.html)

## p.s.

1. 单个文件会转换后保存至同目录，格式为xxx__converted.xxx，文件夹会保存至 `converted_files` 目录
2. 进度动画可以在同目录下新建一个txt文档并命名为 `no_animation_plz.txt` 来禁用（文档内容随意）
3. 除非出问题，不然程序不会自动退出
4. 我不会代码，孩子不懂事写着玩的
5. 不管发生什么，请尽可能认为这是正常的


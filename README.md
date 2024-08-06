# FFmpeg GUI Converter
不太实用的ffmpeg gui，能实现基本的格式转换
<br><br>
![image](https://github.com/user-attachments/assets/65b4883c-c227-4119-8872-695ea72b7bdb)

- [English](README_en.md)

## 特点

- 能处理大部分简单的FFmpeg任务
- 可以处理文件目录
- 可添加额外参数
- 进度条(简陋的)
- 多余的动画
- ~~传奇依托白话菜比代码~~

## 安装

### 安装FFmpeg（前置条件）

如果你还没有安装FFmpeg，程序通常会帮你自动下载并安装（需要魔法环境，偶尔需要管理员权限）。如果安装失败，可以通过以下方式进行安装：
#### Windows
- 使用 `winget` ：
  ```shell
  winget install "FFmpeg (Essentials Build)"
  ```
#### Linux
 - 我不会
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
-vf "scale=1280:720,transpose=1" -af "volume=2" -b:v 1M -b:a 320k -c:v libx264 -crf 23
```
具体解释如下：
- `-ss 00:00:10`：从视频的第10秒开始处理
- `-t 00:01:00`：持续处理1分钟
- `-vf "scale=1280:720,transpose=1"`：应用视频过滤器（video filter）
  - `scale=1280:720`：将视频缩放到1280x720像素
  - `transpose=1`：将视频顺时针旋转90度
- `-af "volume=2"`：应用音频过滤器（audio filter）
  - `volume=2`：将音量提高2倍
- `-b:v 1M`: 指定视频码率为1Mbps
- `-b:a 320k`：指定音频码率为320kbps
- `-c:v libx264`：指定视频编码器为 `libx264`
- `-crf 23`：指定恒定速率因子（CRF）为23

更多请参阅：[FFmpeg官方文档](https://ffmpeg.org/ffmpeg.html)

## p.s.

1. 单个文件会转换后保存至同目录，格式为xxx_converted.xxx，文件夹会保存至 `converted_files` 目录
2. 进度动画可以在同目录下新建一个txt文档并命名为 `no_animation_plz.txt` 来禁用（文档内容随意）
3. 除非出问题，不然程序不会自动退出。一般情况下显示Finished会伴随着动画结束，如果执行后立即显示Finished且窗口动画持续运行则说明ffmpeg出错了，这个时候直接关了吧。
4. 我不会代码，孩子不懂事写着玩的
5. 不管发生什么，请尽可能认为这是正常的


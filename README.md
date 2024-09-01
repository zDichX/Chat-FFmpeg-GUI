# Chat FFmpeg GUI
不太实用的FFmpeg GUI，能实现基本的格式转换，并能根据自然语言描述来生成命令。
<br><br>

![screenshot](https://github.com/user-attachments/assets/8b783e5e-571e-4a88-9a0e-95f2a2d3f21c)

- [English](README_en.md)

## 特点

- 能处理大部分简单的FFmpeg任务
- 可以处理文件目录
- 自动填写参数
- 显示进度(简陋的)
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
- 或[下载ffmpeg预编译文件](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z)并解压到同目录，确保文件名为"ffmpeg"开头。
#### Linux
 - 兼容性未知，不建议Linux直接运行

### 方法一：下载预编译的可执行文件

1. 访问 [Releases 页面](../../releases)
2. 下载并解压最新版本的 `.zip` 文件
3. 运行程序

### 方法二：Git Clone

1. 不用教

## 用法

1. 拖拽文件到窗口或选择文件
2. 选择目标格式
3. （可选）生成参数：
   - 在`config.json`中填入你的 **url** 和 **api_key** ，你可以从 [OpenAI官网](https://platform.openai.com/api-keys) 获取，如果有困难，也可以使用中转服务，例如：
      - [FREE-CHATGPT-API](https://github.com/popjane/free_chatgpt_api)
      - [GPT-API-free](https://github.com/chatanywhere/GPT_API_free)
   - 用自然语言简单描述你的需求，例如：
      - 只转换前10秒
      - 保持音频流，压缩视频流
      - 将视频旋转180度
   - 点击 **Generate** 生成命令
4. 点击 **Execute** 按钮
5. 等待转换完成



## p.s.

1. 单个文件会转换后保存至同目录，格式为xxx_converted.xxx，文件夹会保存至 `converted_files` 目录
2. 现版本默认关闭执行时的窗口动画，若想重新启用则需要将config.json中的animation值改为true。
3. 除非出问题，不然程序不会自动退出。如果执行后立即显示Finished，且窗口动画持续运行，则有两种可能：任务瞬间完成，**或ffmpeg出错**，此时不应该继续等待。
4. 我不会代码，孩子不懂事写着玩的
5. 不管发生什么，请尽可能认为这是正常的

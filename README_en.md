# Chat FFmpeg GUI
A less practical FFmpeg GUI that can perform basic format conversions and generate commands based on natural language descriptions.
<br><br>

![screenshot](https://github.com/user-attachments/assets/8b783e5e-571e-4a88-9a0e-95f2a2d3f21c)

## Features

- [x] Handles most simple FFmpeg tasks
- [x] Can process directories
- [x] Autofill parameters
- [x] Progress bar (rudimentary)
- [x] Extra animations

## Installation

### Installing FFmpeg (Prerequisite)

If you haven’t installed FFmpeg yet, the program will usually download and install it automatically in the background (after installation, it will exit automatically, and you can restart). If the installation fails, you can install it manually:

#### Windows
- Using `winget`:

  ```shell
  winget install "FFmpeg (Essentials Build)"
  ```
- You can either [download the precompiled ffmpeg files](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z) and extract them to the same directory, ensuring the filename starts with "ffmpeg".


#### Linux
- Compatibility unknown; not recommended for direct execution on Linux.

### Method 1: Download Precompiled Executable

1. Visit the [Releases Page](../../releases)
2. Download and unzip the latest `.zip` file
3. Run the program

### Method 2: Git Clone

1. You should know how

## Usage

1. Drag and drop files into the window (recommended), or choose files/select a path.
2. Select the target format.
3. (Optional) Set parameters:
   - Fill in your `url` and `api_key` in `config.json`. You can obtain these from the [OpenAI website](https://platform.openai.com/api-keys). If you encounter difficulties, you can use proxy services such as:
      - [FREE-CHATGPT-API](https://github.com/popjane/free_chatgpt_api)
      - [GPT-API-free](https://github.com/chatanywhere/GPT_API_free)
      - ……
   - Describe your requirements in natural language, for example:

      - Mute the video
      - Compress the video with H.264
      - Rotate the video 180 degrees
      - Trim the first 10 seconds of the video
      - ……
   - Click `Generate` to create the command.
4. Click the `Execute` button.
5. Wait for the conversion to complete.

## P.S.

1. Single files will be saved in the same directory with the format `xxx_converted.xxx`, and folders will be saved in the `converted_files` directory.
2. The program will not automatically exit unless something goes wrong. Normally, If `Finished` is displayed immediately after execution and the window animation continues, it means finished easily, **OR FFmpeg encountered an error**. You can close it at this point.
3. I don't know coding, this is just a project for fun.
4. No matter what happens, try to assume it's normal.

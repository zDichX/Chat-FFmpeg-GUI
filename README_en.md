# FFmpeg GUI Converter

A not-so-practical FFmpeg GUI that can perform basic format conversions.
<br><br>
![image](https://github.com/user-attachments/assets/65b4883c-c227-4119-8872-695ea72b7bdb)

## Features

- Handles most simple FFmpeg tasks
- Can process directories
- Allows additional parameters
- Progress bar (rudimentary)
- Extra animations

## Installation

### Installing FFmpeg (Prerequisite)

If you don't have FFmpeg installed, the program usually helps you download and install it automatically (sometimes administrative privileges). If the installation fails, you can install it manually:

#### Windows
- Using `winget`:
  ```shell
  winget install "FFmpeg (Essentials Build)"
  ```

#### Linux
- Not sure how to do it

### Method 1: Download Precompiled Executable

1. Visit the [Releases Page](../../releases)
2. Download the latest `.exe` program
3. Run the program

### Method 2: Git Clone

1. You should know how

## Usage

1. Drag and drop files into the window or select files
2. Enter parameters (optional)
3. Select the target format
4. Click the **Execute** button
5. Wait for the conversion to complete

### Parameter Examples

#### Input
```shell
-ss 00:00:10 -t 00:01:00
```
#### Output
```shell
-vf "scale=1280:720,transpose=1" -af "volume=2" -b:v 1M -b:a 320k -c:v libx264 -crf 23
```
Explanation:
- `-ss 00:00:10`: Start processing from the 10th second of the video
- `-t 00:01:00`: Process for 1 minute
- `-vf "scale=1280:720,transpose=1"`: Apply video filters
  - `scale=1280:720`: Scale the video to 1280x720 pixels
  - `transpose=1`: Rotate the video 90 degrees clockwise
- `-af "volume=2"`: Apply audio filters
  - `volume=2`: Increase volume by 2 times
- `-b:v 1M`: Set video bitrate to 1Mbps
- `-b:a 320k`: Set audio bitrate to 320kbps
- `-c:v libx264`: Use `libx264` video codec
- `-crf 23`: Set Constant Rate Factor to 23

For more details, see the [FFmpeg Documentation](https://ffmpeg.org/ffmpeg.html).

## P.S.

1. Single files will be saved in the same directory with the format xxx_converted.xxx, and folders will be saved in the `converted_files` directory.
2. To disable progress animations, create a text file named `no_animation_plz.txt` in the same directory (contents of the file don't matter).
3. The program will not automatically exit unless something goes wrong. Normally, "Finished" will be displayed with the animation ending. If "Finished" is displayed immediately after execution and the window animation continues, it means FFmpeg encountered an error. You can close it at this point.
4. I don't know coding, this is just a project for fun.
5. No matter what happens, try to assume it's normal.

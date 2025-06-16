import argparse  # type: ignore
import os  # type: ignore
import os.path  # type: ignore
import subprocess  # type: ignore
import sys  # type: ignore
import tkinter as tk  # type: ignore
import urllib.parse  # type: ignore
import zipfile  # type: ignore
from io import BytesIO  # type: ignore
from threading import Thread  # type: ignore
from tkinter import ttk, messagebox  # type: ignore
import requests  # type: ignore

from app.updater_app import start_app  # type: ignore
from app.utils.validator import *

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='自动更新程序/Auto Updater',
        formatter_class=argparse.RawTextHelpFormatter  # 保留格式
    )

    # 添加带中英说明的参数
    parser.add_argument(
        '--download_url',
        required=True,
        help='下载文件的URL / Download URL\n(例如/example: http://example.com/update.zip)'
    )
    parser.add_argument(
        '--restart_exe_path',
        help='更新完成后重启的exe路径 / Path to restart after update\n(例如/example: C:/app/main.exe)'
    )
    parser.add_argument(
        '--extract_path',
        help='解压文件的目标路径（可选） / Extraction path (optional)\n(默认/default: 当前目录/current directory)',
        default='.'
    )
    parser.add_argument(
        '--show',
        help='是否显示UI界面（True/False） / Show UI (True/False)\n(默认/default: True)',
        type=str,
        default='True'
    )

    # 自定义帮助信息
    parser._positionals.title = "必选参数/Required arguments"
    parser._optionals.title = "可选参数/Optional arguments"

    # 添加使用示例
    parser.epilog = """使用示例/Examples:
  显示UI界面/With UI:
    updater.exe --download_url=http://example.com/update.zip

  静默模式/Silent mode:
    updater.exe --download_url=http://example.com/update.zip --show=False

  指定解压路径和重启程序/With extract path and restart:
    updater.exe --download_url=http://example.com/update.zip \\
                --extract_path=C:/app \\
                --restart_exe_path=C:/app/main.exe
"""

    try:
        args = parser.parse_args()

        # 如果只输入--help，则显示帮助信息并退出
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(0)

        validate_arguments(args)

        start_app(args)

    except Exception as e:
        messagebox.showerror("错误/Error",
                             f"更新失败/Update failed: {str(e)}\n\n使用方法/Usage:\n{parser.format_help()}")
        sys.exit(1)

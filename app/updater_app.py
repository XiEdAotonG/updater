import os
import os.path
import subprocess
import sys
import time
import tkinter as tk
import zipfile
from io import BytesIO
from threading import Thread
from tkinter import ttk, messagebox

import requests


class UpdaterApp:
    def __init__(self, root, download_url, restart_exe_path=None, extract_path='.'):
        self.root = root
        self.download_url = download_url
        self.restart_exe_path = os.path.abspath(restart_exe_path) if restart_exe_path else None  # 确保使用绝对路径
        self.extract_path = extract_path  # 添加解压路径属性
        self.total_size = 0
        self.downloaded_size = 0

        self.setup_ui()

    def setup_ui(self):
        self.root.title("自动更新")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        # 设置窗口图标 (可选)
        try:
            self.root.iconbitmap(default='updater_logo.ico')
        except:
            pass

        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="自动更新", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))

        # 下载进度条
        self.download_label = ttk.Label(main_frame, text="下载进度: 0%")
        self.download_label.pack(anchor=tk.W)

        self.download_progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.download_progress.pack(fill=tk.X, pady=(0, 20))

        # 解压进度条
        self.extract_label = ttk.Label(main_frame, text="安装进度: 等待下载完成...")
        self.extract_label.pack(anchor=tk.W)

        self.extract_progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.extract_progress.pack(fill=tk.X)

        # 状态信息
        self.status_label = ttk.Label(main_frame, text="准备下载更新文件...", foreground="blue")
        self.status_label.pack(pady=(10, 0))

        # 开始下载
        self.start_download()

    def start_download(self):
        self.status_label.config(text="正在连接服务器...", foreground="blue")
        Thread(target=self.download_file, daemon=True).start()

    def download_file(self):
        try:
            # 获取文件大小
            with requests.get(self.download_url, stream=True) as r:
                r.raise_for_status()
                self.total_size = int(r.headers.get('content-length', 0))

                # 更新UI
                self.root.after(0, lambda: self.status_label.config(
                    text=f"正在下载更新，文件大小【{self.format_size(self.total_size)}】",
                    foreground="blue"
                ))

                # 下载文件
                buffer = BytesIO()
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        buffer.write(chunk)
                        self.downloaded_size += len(chunk)

                        # 更新进度条
                        progress = int((self.downloaded_size / self.total_size) * 100)
                        self.root.after(0, self.update_download_progress, progress)

                # 下载完成
                self.root.after(0, lambda: self.status_label.config(
                    text="下载完成，准备解压...",
                    foreground="green"
                ))

                # 开始解压
                self.extract_file(buffer)

        except Exception as e:
            message = str(e)
            self.root.after(0, lambda: self.show_error(f"下载失败: {str(message)}"))
            print(f"下载失败: {str(message)}")

    def extract_file(self, buffer):
        try:
            buffer.seek(0)

            with zipfile.ZipFile(buffer) as zip_ref:
                # 解决中文文件名乱码问题
                for file in zip_ref.infolist():
                    file.filename = file.filename.encode('cp437').decode('gbk')  # 或者用 'utf-8' 根据实际情况调整
                file_list = zip_ref.infolist()

                self.root.after(0, lambda: self.status_label.config(
                    text=f"正在解压 {len(file_list)} 个文件...",
                    foreground="blue"
                ))

                self.root.after(0, lambda: self.extract_progress.config(maximum=len(file_list)))
                # 确保目标目录存在
                os.makedirs(self.extract_path, exist_ok=True)
                for i, file in enumerate(file_list, 1):
                    try:
                        zip_ref.extract(file, self.extract_path)
                    except Exception as e:
                        print(f"解压 {file.filename} 时出错: {e}")

                    self.root.after(0, self.update_extract_progress, i, len(file_list))

                self.root.after(0, self.complete_update)
                time.sleep(1)
                sys.exit(0)

        except Exception as e:
            message = str(e)
            self.root.after(0, lambda: self.show_error(f"解压失败: {str(message)}"))

    def update_download_progress(self, progress):
        self.download_progress['value'] = progress
        self.download_label.config(text=f"下载进度: {progress}%")

    def update_extract_progress(self, current, total):
        progress = (current / total) * 100
        self.extract_progress['value'] = current
        self.extract_label.config(text=f"解压进度: {current}/{total} 文件 ({int(progress)}%)")

    def complete_update(self):
        self.status_label.config(text="更新完成!", foreground="green")

        if self.restart_exe_path:
            # 检查目标程序是否存在
            if os.path.exists(self.restart_exe_path):
                # 延迟1秒后重启程序
                self.root.after(1000, self.restart_application)
            else:
                messagebox.showwarning("警告", f"未找到可执行文件: {self.restart_exe_path}")
                self.root.after(1000, self.root.destroy)
        else:
            # messagebox.showinfo("完成", "更新已成功完成!")
            self.root.after(1000, self.root.destroy)

    def restart_application(self):
        """重启指定的应用程序"""
        try:
            # 关闭当前窗口
            self.root.destroy()

            # 启动目标程序
            if sys.platform == 'win32':
                os.startfile(self.restart_exe_path)
            else:
                subprocess.Popen([self.restart_exe_path])

        except Exception as e:
            messagebox.showerror("错误", f"启动程序失败: {str(e)}")

    def show_error(self, message):
        self.status_label.config(text=message, foreground="red")
        messagebox.showerror("错误", message)
        self.root.after(1000, self.root.destroy)

    @staticmethod
    def format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class SilentUpdater:
    def __init__(self, download_url, restart_exe_path=None, extract_path='.'):
        self.download_url = download_url
        self.restart_exe_path = os.path.abspath(restart_exe_path) if restart_exe_path else None
        self.extract_path = extract_path
        self.total_size = 0
        self.downloaded_size = 0

    def run(self):
        try:
            self.download_and_extract()
            self.restart_if_needed()
        except Exception as e:
            print(f"更新失败: {str(e)}")
            sys.exit(1)

    def download_and_extract(self):
        # 下载文件
        with requests.get(self.download_url, stream=True) as r:
            r.raise_for_status()
            self.total_size = int(r.headers.get('content-length', 0))
            print(f"开始下载更新，文件大小: {self.format_size(self.total_size)}")
            buffer = BytesIO()
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    buffer.write(chunk)
                    self.downloaded_size += len(chunk)
                    progress = int((self.downloaded_size / self.total_size) * 100)
                    print(f"下载进度: {progress}%", end='\r')
            print("\n下载完成，开始解压...")
            self.extract_file(buffer)

    def extract_file(self, buffer):
        buffer.seek(0)
        with zipfile.ZipFile(buffer) as zip_ref:
            file_list = zip_ref.infolist()
            print(f"正在解压 {len(file_list)} 个文件...")

            os.makedirs(self.extract_path, exist_ok=True)
            for i, file in enumerate(file_list, 1):
                try:
                    # 解决中文文件名乱码问题
                    file.filename = file.filename.encode('cp437').decode('gbk')
                    zip_ref.extract(file, self.extract_path)
                except Exception as e:
                    print(f"解压 {file.filename} 时出错: {e}")

                progress = int((i / len(file_list)) * 100)
                print(f"解压进度: {progress}%", end='\r')

            print("\n解压完成!")

    def restart_if_needed(self):
        if self.restart_exe_path and os.path.exists(self.restart_exe_path):
            print(f"正在重启应用程序: {self.restart_exe_path}")
            if sys.platform == 'win32':
                os.startfile(self.restart_exe_path)
            else:
                subprocess.Popen([self.restart_exe_path])

    @staticmethod
    def format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


def start_app(args):
    # 处理show参数
    show_ui = args.show.lower() in ('true', '1', 't', 'y', 'yes')

    if show_ui:
        # 创建GUI
        root = tk.Tk()
        UpdaterApp(root, args.download_url, args.restart_exe_path, args.extract_path)
        root.mainloop()
    else:
        # 静默模式
        updater = SilentUpdater(args.download_url, args.restart_exe_path, args.extract_path)
        updater.run()
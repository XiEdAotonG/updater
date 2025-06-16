import os
import os.path
import sys
import urllib.parse
from tkinter import messagebox


def validate_arguments(args):
    """校验传入参数的有效性"""
    errors = []

    # 校验URL
    if not is_valid_url(args.download_url):
        errors.append(f"无效的下载URL: {args.download_url}")
    else:
        print(f"下载URL: {args.download_url}")
    #     from urllib.parse import quote
    #     args.download_url = quote(args.download_url, safe=':/?&=@+$,;%')
    # 如果提供了重启exe路径，则校验
    if args.restart_exe_path:
        args.restart_exe_path = validate_exe_path(args.restart_exe_path)
        if not args.restart_exe_path:
            errors.append("指定的重启程序不存在或不是有效的exe文件")

    # 校验解压路径
    args.extract_path = validate_extract_path(args.extract_path)
    if not args.extract_path:
        errors.append("指定的解压路径无效或没有写入权限")

    if errors:
        messagebox.showerror("参数错误", "\n".join(errors))
        sys.exit(1)


def validate_extract_path(path):
    """校验解压路径是否存在，如果不存在则创建，并检查写入权限"""
    try:
        # 转换为绝对路径
        abs_path = os.path.abspath(path)

        # 如果路径不存在，尝试创建
        if not os.path.exists(abs_path):
            os.makedirs(abs_path, exist_ok=True)

        # 检查是否是目录
        if not os.path.isdir(abs_path):
            return None

        # 检查写入权限
        test_file = os.path.join(abs_path, ".write_test")
        try:
            # 尝试创建文件测试写入权限
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return abs_path
        except:
            return None
    except Exception as e:
        print(f"解压路径校验错误: {e}")
        return None


def is_valid_url(url):
    """检查URL是否有效"""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except ValueError:
        return False


def is_url_encoded(url):
    """检查URL是否已经被编码"""
    decoded = urllib.parse.unquote(url)
    return decoded != url


def encode_url(url):
    """对URL进行编码处理（仅对未编码的部分）"""
    if is_url_encoded(url):
        return url

    parsed = urllib.parse.urlparse(url)
    encoded_path = urllib.parse.quote(parsed.path)
    encoded_query = urllib.parse.quote_plus(parsed.query) if parsed.query else ''
    encoded_fragment = urllib.parse.quote(parsed.fragment) if parsed.fragment else ''

    return urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        encoded_path,
        parsed.params,
        encoded_query,
        encoded_fragment
    ))


def validate_exe_path(exe_path):
    """校验exe路径是否存在并转换为绝对路径"""
    try:
        # 转换为绝对路径并规范化
        abs_path = os.path.abspath(exe_path)

        # 检查路径是否存在
        if not os.path.exists(abs_path):
            return None

        # 检查是否是exe文件 (Windows) 或可执行文件 (Unix)
        if sys.platform == 'win32':
            if not abs_path.lower().endswith('.exe'):
                return None
        else:
            if not os.access(abs_path, os.X_OK):
                return None

        return abs_path
    except Exception:
        return None

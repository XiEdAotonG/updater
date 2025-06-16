# Auto Updater

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

一个轻量级的Python自动更新程序，支持静默更新和带UI界面的更新操作，适用于Windows应用程序的自动更新场景。

## 功能特性

- 从指定URL下载更新文件
- 自动解压ZIP格式的更新包
- 支持静默模式（无UI界面）
- 更新完成后自动重启应用程序
- 多语言支持（中英文）
- 命令行参数配置灵活

## 安装要求

- Python 3.11+
- 依赖库：
  ```
  pip install -r requirements.txt
  ```

## 使用说明

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--download_url` | **必须**<br>下载文件的URL | `http://example.com/update.zip` |
| `--restart_exe_path` | 更新完成后重启的exe路径 | `C:/app/main.exe` |
| `--extract_path` | 解压文件的目标路径<br>默认: 当前目录 | `C:/app` |
| `--show` | 是否显示UI界面<br>默认: True<br>可选值: True/False | `False` |

### 使用示例

#### 显示UI界面
```bash
updater.exe --download_url=http://example.com/update.zip
```

#### 静默模式（无UI）
```bash
updater.exe --download_url=http://example.com/update.zip --show=False
```

#### 指定解压路径和重启程序
```bash
updater.exe --download_url=http://example.com/update.zip \
            --extract_path=C:/app \
            --restart_exe_path=C:/app/main.exe
```

## 集成到您的应用

1. 在您的主应用程序中检测更新
2. 当需要更新时，通过命令行参数启动更新程序
3. 主程序退出，让更新程序接管后续操作

示例调用代码：
```python
import subprocess
import sys

# 构造更新命令
command = [
    "updater.exe",
    "--download_url=http://your-server/update-v2.0.zip",
    "--extract_path=C:/YourApp",
    "--restart_exe_path=C:/YourApp/YourApp.exe",
    "--show=True"
]

# 启动更新程序并退出当前应用
subprocess.Popen(command)
sys.exit(0)
```

## 工作原理

1. 程序启动，解析命令行参数
2. 根据`--show`参数决定是否显示UI界面
3. 从指定URL下载更新文件（ZIP、RAR格式）
4. 将文件解压到目标目录（`--extract_path`）
5. 如果指定了`--restart_exe_path`，则重启该程序
6. 清理临时文件并退出

## 注意事项

1. 确保更新程序有目标目录的写入权限
2. 更新包必须是ZIP格式
3. 主程序退出后才能成功覆盖文件
4. 静默模式(`--show=False`)适用于后台更新
5. 更新程序本身不应放在需要更新的目录中

## 许可证

本项目采用 [MIT 许可证](LICENSE)

---

**温馨提示**：在生产环境中使用前，请充分测试更新流程，确保在各种情况下都能正确恢复应用程序。

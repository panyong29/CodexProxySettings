# CodexProxySettings

A small Windows utility for setting Codex proxy variables and managing the ChatGPT desktop app.

[Download the native Windows app](https://github.com/panyong29/CodexProxySettings/releases/latest) · [View all releases](https://github.com/panyong29/CodexProxySettings/releases)

## Quick start

1. Download **CodexProxySettings.exe** from the [latest release](https://github.com/panyong29/CodexProxySettings/releases/latest).
2. Save it somewhere easy to find, such as your Downloads folder, then double-click it.
3. Start your proxy client. Choose a preset or type your own HTTP/HTTPS proxy address:
   - **Clash HTTP:** `http://127.0.0.1:7890`
   - **V2Ray HTTP:** `http://127.0.0.1:10809`

   These are common defaults. Your client may use a different port; check its settings if the connection does not work.
4. Click **Save**. The app updates `%USERPROFILE%\.codex\.env`.
5. Completely quit and reopen Codex so it loads the new settings.

## Buttons

| Button | What it does |
| --- | --- |
| **Clear Config** | Removes `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` from the active Codex environment file. |
| **Save** | Saves the selected proxy to the active Codex environment file. |
| **Save As** | Saves a copy to a file you choose. This does not change Codex's active settings. |
| **Close ChatGPT** | Requests a normal close. If ChatGPT stays in the system tray, the app asks before force-quitting it. Force-quitting may lose unsaved work. |
| **Start ChatGPT** | Opens the installed ChatGPT Windows app. |

The app preserves unrelated lines in the environment file. Restart Codex after saving or clearing settings.

## Choose a build

- **Native C# build — `CodexProxySettings.exe`:** small WinForms app; requires the .NET Framework available on Windows.
- **Python build — `CodexProxySettings_Python.exe`:** single executable with the Python runtime bundled; larger download.

The native C# executable is available on the [Releases page](https://github.com/panyong29/CodexProxySettings/releases).

> **Security note:** The release executables are not code-signed. Security software may flag unsigned applications. If one is blocked, check the security product's detection details before deciding what to do.

## Build from source

### Native C# version

On Windows with the .NET Framework C# compiler (`csc.exe`):

```powershell
csc /nologo /target:winexe /optimize+ /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /out:CodexProxySettings.exe ProxyGui.cs
```

### Python version

Install Python, then package the GUI as a single executable with PyInstaller:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name CodexProxySettings_Python codex_proxy_gui.py
```

---

# CodexProxySettings（中文说明）

这是一个 Windows 小工具，用于设置 Codex 代理并管理 ChatGPT 桌面程序。

[下载原生 Windows 版](https://github.com/panyong29/CodexProxySettings/releases/latest) · [查看全部版本](https://github.com/panyong29/CodexProxySettings/releases)

## 快速开始

1. 从[最新发布页](https://github.com/panyong29/CodexProxySettings/releases/latest)下载 **CodexProxySettings.exe**。
2. 将文件保存到容易找到的位置（例如“下载”文件夹），然后双击运行。
3. 先启动代理客户端，再选择预设或手动输入 HTTP/HTTPS 代理地址：
   - **Clash HTTP：** `http://127.0.0.1:7890`
   - **V2Ray HTTP：** `http://127.0.0.1:10809`

   这是常见默认端口。你的客户端可能使用其他端口；如果连接失败，请检查客户端设置。
4. 点击**保存**。程序会更新 `%USERPROFILE%\.codex\.env`。
5. 完全退出并重新打开 Codex，让新设置生效。

## 按钮说明

| 按钮 | 功能 |
| --- | --- |
| **清除配置** | 从 Codex 当前使用的环境文件中移除 `HTTP_PROXY`、`HTTPS_PROXY` 和 `NO_PROXY`。 |
| **保存** | 将选中的代理地址写入 Codex 当前使用的环境文件。 |
| **另存** | 将配置副本保存到你选择的文件；不会更改 Codex 当前使用的设置。 |
| **关闭 ChatGPT** | 先请求正常关闭。如果 ChatGPT 仍在系统托盘，程序会询问是否强制退出。强制退出可能丢失未保存的工作。 |
| **启动 ChatGPT** | 打开已安装的 ChatGPT Windows 应用。 |

程序会保留环境文件中的其他配置行。保存或清除后，请重新启动 Codex。

## 选择版本

- **C# 原生版 — `CodexProxySettings.exe`：** 体积小的 WinForms 程序，需要 Windows 上的 .NET Framework。
- **Python 版 — `CodexProxySettings_Python.exe`：** 单文件程序，已包含 Python 运行环境，下载体积较大。

C# 原生 exe 可从 [Releases 发布页](https://github.com/panyong29/CodexProxySettings/releases)下载。

> **安全提示：** 发布的 exe 尚未进行代码签名，安全软件可能会提示风险。如果被拦截，请先查看安全软件显示的检测详情，再决定如何处理。

## 从源码构建

### C# 原生版

在安装了 .NET Framework C# 编译器（`csc.exe`）的 Windows 上运行：

```powershell
csc /nologo /target:winexe /optimize+ /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /out:CodexProxySettings.exe ProxyGui.cs
```

### Python 版

安装 Python 后，使用 PyInstaller 将图形界面打包成单文件 exe：

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name CodexProxySettings_Python codex_proxy_gui.py
```

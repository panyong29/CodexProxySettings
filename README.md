# Codex Proxy GUI

A small Windows desktop utility for configuring Codex proxy settings and managing the ChatGPT desktop app.

## Getting started (for Windows beginners)

1. Open the [latest release](https://github.com/panyong29/Codex_proxy_gui/releases/latest) and download `CodexProxySettings.exe`.
2. Save the file somewhere easy to find, such as your Downloads folder, then double-click it to open the app.
3. Start your proxy client first. Choose **Clash HTTP** (`http://127.0.0.1:7890`) or **V2Ray HTTP** (`http://127.0.0.1:10809`). These are common defaults; if your proxy client uses another port, select the address box and type the correct URL.
4. Click **Save**. The app updates `%USERPROFILE%\.codex\.env`. Completely quit and reopen Codex for the change to take effect.
5. Use **Clear Config** to remove `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` entries from the Codex environment file. Use **Save As** to save a copy to another location; this does not change Codex's active config.

The **Close ChatGPT** button first asks the app to close normally. If ChatGPT remains in the system tray, the app asks before force-quitting it; unsaved work may be lost. **Start ChatGPT** opens the installed Windows app.

## Downloads and project files

- `CodexProxySettings.exe` — compact native C# WinForms build. It uses the .NET Framework installed on Windows.
- `CodexProxySettings_Python.exe` — single-file Python build with Python bundled.
- `ProxyGui.cs` — C# source.
- `codex_proxy_gui.py` — Python source.

The C# executable is published on the [Releases page](https://github.com/panyong29/Codex_proxy_gui/releases).

## Build from source

To compile the native C# version on Windows with the .NET Framework C# compiler:

```powershell
csc /nologo /target:winexe /optimize+ /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /out:CodexProxySettings.exe ProxyGui.cs
```

To package the Python version as a single GUI executable, install Python and PyInstaller, then run:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name CodexProxySettings_Python codex_proxy_gui.py
```

---

# Codex Proxy GUI（中文说明）

这是一个 Windows 桌面小工具，用来设置 Codex 代理并管理 ChatGPT 桌面程序。

## 新手使用步骤

1. 打开[最新发布页](https://github.com/panyong29/Codex_proxy_gui/releases/latest)，下载 `CodexProxySettings.exe`。
2. 把文件保存到容易找到的位置（例如“下载”文件夹），双击运行。
3. 先启动你的代理客户端，再选择 **Clash HTTP**（`http://127.0.0.1:7890`）或 **V2Ray HTTP**（`http://127.0.0.1:10809`）。这两个是常见默认端口；如果客户端使用其他端口，可直接在代理地址框中输入完整地址。
4. 点击**保存**。程序会修改 `%USERPROFILE%\.codex\.env`。请完全退出并重新打开 Codex，设置才会生效。
5. 点击**清除配置**会从 Codex 环境文件中移除 `HTTP_PROXY`、`HTTPS_PROXY` 和 `NO_PROXY` 配置。点击**另存**可以把配置副本保存到其他位置，不会更改 Codex 当前使用的配置。

**关闭 ChatGPT** 会先尝试正常关闭。如果 ChatGPT 仍留在系统托盘，程序会先询问，再强制退出；强制退出可能丢失未保存的内容。**启动 ChatGPT** 会打开已安装的 Windows 应用。

## 下载文件与项目源码

- `CodexProxySettings.exe`：体积小的 C# WinForms 原生版本，使用 Windows 自带的 .NET Framework。
- `CodexProxySettings_Python.exe`：包含 Python 运行环境的单文件版本。
- `ProxyGui.cs`：C# 源码。
- `codex_proxy_gui.py`：Python 源码。

C# exe 发布在 [GitHub Releases 页面](https://github.com/panyong29/Codex_proxy_gui/releases)。

## 从源码构建

在 Windows 上使用 .NET Framework C# 编译器构建原生版本：

```powershell
csc /nologo /target:winexe /optimize+ /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /out:CodexProxySettings.exe ProxyGui.cs
```

安装 Python 和 PyInstaller 后，可用以下命令打包 Python 单文件 GUI 程序：

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name CodexProxySettings_Python codex_proxy_gui.py
```

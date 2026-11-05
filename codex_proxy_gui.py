import ctypes
import os
import re
import subprocess
import sys
import time
import tkinter as tk
from ctypes import wintypes
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urlsplit


ENV_FILE = Path.home() / ".codex" / ".env"
DEFAULTS = {
    "Clash HTTP — http://127.0.0.1:7890": "http://127.0.0.1:7890",
    "V2Ray HTTP — http://127.0.0.1:10809": "http://127.0.0.1:10809",
}
CHATGPT_AUMID = "OpenAI.Codex_2p2nqsd0c76g0!App"


def read_proxy():
    try:
        for line in ENV_FILE.read_text(encoding="utf-8-sig").splitlines():
            match = re.match(r'^\s*HTTP_PROXY\s*=\s*"?([^\"]*)"?\s*$', line, re.I)
            if match:
                return match.group(1)
    except (OSError, UnicodeError):
        pass
    return next(iter(DEFAULTS.values()))


def replace_entry(lines, key, value):
    escaped = re.escape(key)
    old = re.compile(rf"^\s*(?:{escaped}\s*=|#\s*(?:duplicate\s+)?{escaped}(?:\s|=))", re.I)
    lines[:] = [line for line in lines if not old.match(line)]
    if value is not None:
        lines.append(f'{key}="{value}"')


def valid_proxy(value):
    try:
        parsed = urlsplit(value)
        return parsed.scheme.lower() in ("http", "https") and bool(parsed.hostname) and not any(c in value for c in '\r\n"')
    except ValueError:
        return False


def close_chatgpt():
    """Ask ChatGPT windows to close; never force-terminate the process."""
    if os.name != "nt":
        messagebox.showerror("ChatGPT", "关闭 ChatGPT 的进程控制仅支持 Windows。")
        return

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    PROCESS_TERMINATE = 0x0001
    WM_CLOSE = 0x0010
    target_pids = set()
    parent_by_pid = {}
    kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel32.TerminateProcess.restype = wintypes.BOOL
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.PostMessageW.restype = wintypes.BOOL

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", ctypes.c_ulong), ("cntUsage", ctypes.c_ulong),
            ("th32ProcessID", ctypes.c_ulong), ("th32DefaultHeapID", ctypes.c_size_t),
            ("th32ModuleID", ctypes.c_ulong), ("cntThreads", ctypes.c_ulong),
            ("th32ParentProcessID", ctypes.c_ulong), ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", ctypes.c_ulong), ("szExeFile", ctypes.c_wchar * 260),
        ]

    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
    if snapshot == wintypes.HANDLE(-1).value:
        messagebox.showerror("ChatGPT", "无法读取 Windows 进程列表。")
        return
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        ok = kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
        while ok:
            if entry.szExeFile.lower() == "chatgpt.exe":
                target_pids.add(entry.th32ProcessID)
                parent_by_pid[entry.th32ProcessID] = entry.th32ParentProcessID
            ok = kernel32.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(snapshot)

    if not target_pids:
        messagebox.showinfo("ChatGPT", "未找到正在运行的 ChatGPT 程序。")
        return
    root_pids = {pid for pid, parent in parent_by_pid.items() if parent not in target_pids}

    sent = set()
    enum_callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows.argtypes = [enum_callback_type, wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL

    @enum_callback_type
    def visit_window(hwnd, _):
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in root_pids and user32.IsWindowVisible(hwnd):
            user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
            sent.add(pid.value)
        return True

    user32.EnumWindows(visit_window, 0)
    time.sleep(5)
    still_running = []
    for pid in root_pids:
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if handle:
            still_running.append(pid)
            kernel32.CloseHandle(handle)
    if still_running:
        force = messagebox.askyesno("确认强制退出", "ChatGPT 仍在系统托盘运行。是否强制退出 ChatGPT 及其辅助进程？未保存的内容可能丢失。", icon="warning")
        if force:
            for pid in target_pids:
                handle = kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
                if handle:
                    kernel32.TerminateProcess(handle, 1)
                    kernel32.CloseHandle(handle)
            deadline = time.monotonic() + 6
            remaining = []
            while time.monotonic() < deadline:
                remaining = []
                for pid in root_pids:
                    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
                    if handle:
                        remaining.append(pid)
                        kernel32.CloseHandle(handle)
                if not remaining:
                    break
                time.sleep(0.25)
            if remaining:
                messagebox.showwarning("ChatGPT", "ChatGPT 主程序仍在运行；请稍后重试。")
            else:
                messagebox.showinfo("ChatGPT", "ChatGPT 已退出。")
        else:
            messagebox.showinfo("ChatGPT", "ChatGPT 仍在系统托盘运行。")
    elif sent:
        messagebox.showinfo("ChatGPT", "ChatGPT 已正常关闭。")
    else:
        messagebox.showwarning("ChatGPT", "没有找到可关闭的 ChatGPT 窗口，请手动退出程序。")


def find_chatgpt_shortcut():
    roots = [
        Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
        Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
        Path.home() / "Desktop",
    ]
    for root in roots:
        try:
            if root.is_dir():
                for candidate in root.rglob("*ChatGPT*.lnk"):
                    return candidate
        except OSError:
            continue
    known = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/ChatGPT/ChatGPT.exe",
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "ChatGPT/ChatGPT.exe",
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "ChatGPT/ChatGPT.exe",
    ]
    return next((path for path in known if path.is_file()), None)


class ProxyApp:
    def __init__(self, root):
        self.root = root
        root.title("Codex Proxy Settings")
        root.resizable(False, False)
        root.geometry("510x228")
        root.columnconfigure(0, weight=1)

        close = ttk.Button(root, text="关闭 ChatGPT", command=close_chatgpt)
        close.grid(row=0, column=0, sticky="w", padx=18, pady=(16, 6))

        proxy_row = ttk.Frame(root)
        proxy_row.grid(row=1, column=0, sticky="ew", padx=18, pady=6)
        ttk.Label(proxy_row, text="代理地址：").pack(side="left")
        self.proxy = ttk.Combobox(proxy_row, width=52, values=list(DEFAULTS.keys()))
        saved = read_proxy()
        label = next((name for name, url in DEFAULTS.items() if url == saved), saved)
        self.proxy.set(label)
        self.proxy.pack(side="left", fill="x", expand=True)

        actions = ttk.Frame(root)
        actions.grid(row=2, column=0, sticky="w", padx=18, pady=8)
        ttk.Button(actions, text="清除配置", command=self.clear).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="保存", command=self.save).pack(side="left", padx=8)
        ttk.Button(actions, text="另存", command=self.save_as).pack(side="left", padx=8)

        ttk.Button(root, text="启动 ChatGPT", command=self.start_chatgpt).grid(row=3, column=0, sticky="w", padx=18, pady=(7, 12))

    def selected_proxy(self):
        value = self.proxy.get().strip()
        return DEFAULTS.get(value, value)

    def write_config(self, destination, clear=False):
        proxy = self.selected_proxy()
        if not clear and not valid_proxy(proxy):
            messagebox.showwarning("代理地址无效", "请输入有效地址，例如 http://127.0.0.1:7890")
            return
        try:
            lines = destination.read_text(encoding="utf-8-sig").splitlines() if destination.exists() else []
            replace_entry(lines, "HTTP_PROXY", None if clear else proxy)
            replace_entry(lines, "HTTPS_PROXY", None if clear else proxy)
            replace_entry(lines, "NO_PROXY", None if clear else "localhost,127.0.0.1,::1")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            note = "\n\n请完全退出并重新打开 Codex，使设置生效。" if destination == ENV_FILE and not clear else ""
            messagebox.showinfo("Codex 代理设置", f"已保存到：\n{destination}{note}")
        except (OSError, UnicodeError) as exc:
            messagebox.showerror("保存失败", str(exc))

    def save(self):
        self.write_config(ENV_FILE)

    def clear(self):
        self.write_config(ENV_FILE, clear=True)

    def save_as(self):
        path = filedialog.asksaveasfilename(
            title="另存代理配置", initialdir=str(ENV_FILE.parent), initialfile=".env",
            filetypes=(("环境配置文件", ".env"), ("所有文件", "*.*")),
        )
        if path:
            self.write_config(Path(path))

    def start_chatgpt(self):
        try:
            target = find_chatgpt_shortcut()
            if target is not None and target.suffix.lower() == ".lnk":
                os.startfile(str(target))
            elif target is not None:
                os.startfile(str(target))
            elif os.name == "nt":
                subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{CHATGPT_AUMID}"])
            else:
                messagebox.showerror("ChatGPT", "启动 ChatGPT 的程序查找仅支持 Windows。")
        except OSError as exc:
            messagebox.showerror("启动失败", str(exc))


if __name__ == "__main__":
    app_root = tk.Tk()
    ProxyApp(app_root)
    app_root.mainloop()

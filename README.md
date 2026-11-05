# Codex Proxy GUI

A small Windows desktop utility for configuring Codex proxy environment variables and managing the ChatGPT desktop app.

## Files

- `ProxyGui.cs` — native WinForms implementation. Build with the .NET Framework C# compiler:
  `csc /nologo /target:winexe /optimize+ /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /out:CodexProxySettings.exe ProxyGui.cs`
- `codex_proxy_gui.py` — Python/Tkinter implementation.
- `CodexProxySettings.exe` — compact native Windows build.
- `CodexProxySettings_Python.exe` — single-file Python build with its runtime bundled.

The GUI offers Clash HTTP (`http://127.0.0.1:7890`) and V2Ray HTTP (`http://127.0.0.1:10809`) defaults, manual proxy entry, clear/save/save-as actions, and ChatGPT close/start controls.

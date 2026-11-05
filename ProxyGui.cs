using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows.Forms;

internal static class ProxyGui
{
    private static readonly string EnvFile = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".codex", ".env");
    private static ComboBox proxyBox;
    private sealed class ProxyOption
    {
        public string Name { get; set; }
        public string Url { get; set; }
    }

    [STAThread]
    private static void Main()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        var form = new Form { Text = "Codex Proxy Settings", StartPosition = FormStartPosition.CenterScreen, FormBorderStyle = FormBorderStyle.FixedDialog, MaximizeBox = false, MinimizeBox = true, ClientSize = new Size(510, 228), Font = new Font("Segoe UI", 9F) };
        var grid = new TableLayoutPanel { Dock = DockStyle.Fill, Padding = new Padding(14), ColumnCount = 1, RowCount = 4 };
        grid.RowStyles.Add(new RowStyle(SizeType.Absolute, 43));
        grid.RowStyles.Add(new RowStyle(SizeType.Absolute, 48));
        grid.RowStyles.Add(new RowStyle(SizeType.Absolute, 48));
        grid.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        form.Controls.Add(grid);

        var close = new Button { Text = "关闭 ChatGPT", Width = 140, Height = 30, Anchor = AnchorStyles.Left };
        close.Click += (s, e) => CloseChatGPT();
        grid.Controls.Add(close, 0, 0);

        var proxyRow = new FlowLayoutPanel { Dock = DockStyle.Fill, WrapContents = false, FlowDirection = FlowDirection.LeftToRight, Padding = new Padding(0, 7, 0, 0) };
        proxyRow.Controls.Add(new Label { Text = "代理地址：", AutoSize = true, Padding = new Padding(0, 5, 0, 0) });
        proxyBox = new ComboBox { Width = 390, DropDownStyle = ComboBoxStyle.DropDown, AutoCompleteMode = AutoCompleteMode.SuggestAppend, AutoCompleteSource = AutoCompleteSource.ListItems, DisplayMember = "Name", FormattingEnabled = true };
        proxyBox.Items.AddRange(new object[] {
            new ProxyOption { Name = "Clash HTTP — http://127.0.0.1:7890", Url = "http://127.0.0.1:7890" },
            new ProxyOption { Name = "V2Ray HTTP — http://127.0.0.1:10809", Url = "http://127.0.0.1:10809" }
        });
        string currentProxy = ReadProxy();
        int selectedProxy = -1;
        for (int i = 0; i < proxyBox.Items.Count; i++) if (((ProxyOption)proxyBox.Items[i]).Url == currentProxy) selectedProxy = i;
        if (selectedProxy >= 0) proxyBox.SelectedIndex = selectedProxy; else proxyBox.Text = currentProxy;
        proxyRow.Controls.Add(proxyBox);
        grid.Controls.Add(proxyRow, 0, 1);

        var actions = new FlowLayoutPanel { Dock = DockStyle.Fill, WrapContents = false, FlowDirection = FlowDirection.LeftToRight, Padding = new Padding(0, 5, 0, 0) };
        var clear = new Button { Text = "清除配置", Width = 100, Height = 30 };
        clear.Click += (s, e) => SaveConfig(true, null);
        var save = new Button { Text = "保存", Width = 100, Height = 30 };
        save.Click += (s, e) => SaveConfig(false, EnvFile);
        var saveAs = new Button { Text = "另存", Width = 100, Height = 30 };
        saveAs.Click += (s, e) => { using (var d = new SaveFileDialog { Title = "另存代理配置", Filter = "环境配置文件|.env|所有文件|*.*", FileName = ".env", InitialDirectory = Path.GetDirectoryName(EnvFile) }) if (d.ShowDialog(form) == DialogResult.OK) SaveConfig(false, d.FileName); };
        actions.Controls.Add(clear); actions.Controls.Add(save); actions.Controls.Add(saveAs);
        grid.Controls.Add(actions, 0, 2);

        var start = new Button { Text = "启动 ChatGPT", Width = 140, Height = 32, Anchor = AnchorStyles.Left };
        start.Click += (s, e) => StartChatGPT();
        grid.Controls.Add(start, 0, 3);
        Application.Run(form);
    }

    private static string ReadProxy()
    {
        try { if (File.Exists(EnvFile)) foreach (var line in File.ReadAllLines(EnvFile)) { var m = Regex.Match(line, "^\\s*HTTP_PROXY\\s*=\\s*\"?([^\"]*)\"?\\s*$", RegexOptions.IgnoreCase); if (m.Success) return m.Groups[1].Value; } } catch { }
        return "http://127.0.0.1:7890";
    }

    private static void SaveConfig(bool clear, string target)
    {
        string proxy = proxyBox.SelectedItem is ProxyOption ? ((ProxyOption)proxyBox.SelectedItem).Url : proxyBox.Text.Trim();
        Uri proxyUri;
        if (!clear && (proxy.IndexOf('"') >= 0 || !Uri.TryCreate(proxy, UriKind.Absolute, out proxyUri) || (proxyUri.Scheme != Uri.UriSchemeHttp && proxyUri.Scheme != Uri.UriSchemeHttps) || string.IsNullOrWhiteSpace(proxyUri.Host))) { MessageBox.Show("请输入有效代理地址，例如 http://127.0.0.1:7890", "代理地址无效", MessageBoxButtons.OK, MessageBoxIcon.Warning); return; }
        try
        {
            string destination = target ?? EnvFile;
            var lines = File.Exists(destination) ? File.ReadAllLines(destination, Encoding.UTF8).ToList() : new List<string>();
            SetEntry(lines, "HTTP_PROXY", clear ? null : proxy);
            SetEntry(lines, "HTTPS_PROXY", clear ? null : proxy);
            SetEntry(lines, "NO_PROXY", clear ? null : "localhost,127.0.0.1,::1");
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(destination)));
            File.WriteAllLines(destination, lines, new UTF8Encoding(false));
            MessageBox.Show("已保存到：\r\n" + destination + (destination == EnvFile ? "\r\n\r\n请完全退出并重新打开 Codex，使设置生效。" : ""), "Codex 代理设置", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex) { MessageBox.Show("保存失败：\r\n" + ex.Message, "错误", MessageBoxButtons.OK, MessageBoxIcon.Error); }
    }

    private static void SetEntry(List<string> lines, string key, string value)
    {
        var escaped = Regex.Escape(key);
        var re = new Regex(@"^\s*(?:" + escaped + @"\s*=|#\s*(?:duplicate\s+)?" + escaped + @"(?:\s|=))", RegexOptions.IgnoreCase);
        lines.RemoveAll(line => re.IsMatch(line));
        if (value != null) lines.Add(key + "=\"" + value + "\"");
    }

    private static void CloseChatGPT()
    {
        var ps = Process.GetProcessesByName("ChatGPT");
        if (ps.Length == 0) { MessageBox.Show("未找到正在运行的 ChatGPT 程序。", "ChatGPT"); return; }
        var mainWindows = ps.Where(p => { try { return p.MainWindowHandle != IntPtr.Zero; } catch { return false; } }).ToArray();
        if (mainWindows.Length == 0)
        {
            foreach (var p in ps) p.Dispose();
            MessageBox.Show("ChatGPT 正在运行，但没有找到主窗口；请从程序窗口正常退出。", "ChatGPT", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }
        bool pending = false;
        foreach (var p in mainWindows) try { p.CloseMainWindow(); } catch { pending = true; }
        foreach (var p in mainWindows) try { if (!p.HasExited && !p.WaitForExit(3000)) pending = true; } catch { }
        if (pending)
        {
            var choice = MessageBox.Show("ChatGPT 仍在系统托盘运行。是否强制退出 ChatGPT 及其辅助进程？未保存的内容可能丢失。", "确认强制退出", MessageBoxButtons.YesNo, MessageBoxIcon.Warning);
            if (choice == DialogResult.Yes)
            {
                foreach (var p in Process.GetProcessesByName("ChatGPT"))
                {
                    try { p.Kill(); } catch { }
                    finally { p.Dispose(); }
                }
                var deadline = DateTime.UtcNow.AddSeconds(6);
                pending = mainWindows.Any(p => { try { return !p.HasExited; } catch { return false; } });
                while (pending && DateTime.UtcNow < deadline)
                {
                    System.Threading.Thread.Sleep(250);
                    pending = mainWindows.Any(p => { try { return !p.HasExited; } catch { return false; } });
                }
            }
        }
        var mainSet = new HashSet<Process>(mainWindows);
        foreach (var p in ps) if (!mainSet.Contains(p)) p.Dispose();
        foreach (var p in mainWindows) p.Dispose();
        MessageBox.Show(pending ? "ChatGPT 仍在运行；请从系统托盘退出或稍后重试。" : "ChatGPT 已退出。", "ChatGPT", MessageBoxButtons.OK, pending ? MessageBoxIcon.Warning : MessageBoxIcon.Information);
    }

    private static void StartChatGPT()
    {
        // The installed ChatGPT MSIX package is registered in AppsFolder rather than as a normal exe path.
        try
        {
            Process.Start(new ProcessStartInfo("explorer.exe", "shell:AppsFolder\\OpenAI.Codex_2p2nqsd0c76g0!App") { UseShellExecute = true });
            return;
        }
        catch { }
        string[] roots = { Environment.GetFolderPath(Environment.SpecialFolder.Programs), Environment.GetFolderPath(Environment.SpecialFolder.CommonPrograms), Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory) };
        foreach (var root in roots)
        {
            try { var shortcut = Directory.GetFiles(root, "*ChatGPT*.lnk", SearchOption.AllDirectories).FirstOrDefault(); if (shortcut != null) { Process.Start(new ProcessStartInfo(shortcut) { UseShellExecute = true }); return; } } catch { }
        }
        string[] paths = { Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Programs", "ChatGPT", "ChatGPT.exe"), Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "ChatGPT", "ChatGPT.exe"), Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "ChatGPT", "ChatGPT.exe") };
        string exe = paths.FirstOrDefault(File.Exists);
        try
        {
            if (exe != null) Process.Start(exe);
            else MessageBox.Show("找不到 ChatGPT 桌面程序或开始菜单快捷方式。请先安装 ChatGPT。", "ChatGPT", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        }
        catch (Exception ex) { MessageBox.Show("启动 ChatGPT 失败：\r\n" + ex.Message, "ChatGPT", MessageBoxButtons.OK, MessageBoxIcon.Error); }
    }
}

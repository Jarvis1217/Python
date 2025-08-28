import json
import datetime as dt
import requests
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import messagebox
import webbrowser

def format_duration(seconds):
    """将秒数格式化为 hh:mm:ss"""
    try:
        s = int(seconds)
    except (TypeError, ValueError):
        return "00:00:00"
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    return f"{h:02d}:{m:02d}:{sec:02d}"

def format_pubdate(ts):
    """将时间戳格式化为 yyyy-mm-dd hh:mm:ss（本地时区）"""
    try:
        t = int(ts)
    except (TypeError, ValueError):
        return ""
    return dt.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")

def fetch_bili(cookie_value: str, write_to_file: bool = False):
    url = "https://api.bilibili.com/x/web-interface/wbi/index/top/feed/rcmd"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"

    headers = {
        "User-Agent": user_agent,
        "Cookie": cookie_value or "",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.bilibili.com/",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:
        raise RuntimeError(f"请求或解析失败：{e}")

    items = (payload.get("data") or {}).get("item") or []
    output = []

    for it in items:
        rcmd_reason_obj = it.get("rcmd_reason")
        rcmd_content = ""
        if isinstance(rcmd_reason_obj, dict):
            rcmd_content = rcmd_reason_obj.get("content") or ""

        entry = {
            "bvid": it.get("bvid", ""),
            "title": (it.get("title") or "").strip(),
            "duration": format_duration(it.get("duration")),
            "owner": (it.get("owner") or {}).get("name", ""),
            "pubdate": format_pubdate(it.get("pubdate")),
            "view": (it.get("stat") or {}).get("view", 0),
            "like": (it.get("stat") or {}).get("like", 0),
            "rcmd_reason": rcmd_content,
            "uri": it.get("uri", ""),
        }
        output.append(entry)

    if write_to_file:
        with open("bilibili.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

    return output

def make_full_url(uri: str) -> str:
    if not uri:
        return ""
    uri = uri.strip()
    if uri.startswith("http://") or uri.startswith("https://"):
        return uri
    # 常见情形：以 / 开头的相对路径
    if uri.startswith("/"):
        return "https://www.bilibili.com" + uri
    # 其他情况，直接拼接
    return "https://www.bilibili.com/" + uri

# ----------------- GUI 部分 -----------------
class BiliGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bilibili")
        self.root.geometry("750x600")
        # 存储Cookie
        self.cookie = ""

        # Text area（带滚动条）
        self.text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30)
        self.text.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)

        # 按钮栏
        btn_frame = tk.Frame(root)
        btn_frame.pack(padx=8, pady=(0,8), anchor="e")

        self.get_btn = tk.Button(btn_frame, text="获取", width=12, command=self.on_get)
        self.get_btn.pack(side=tk.LEFT, padx=(0,8))

        self.cfg_btn = tk.Button(btn_frame, text="配置Cookie", width=12, command=self.on_config_cookie)
        self.cfg_btn.pack(side=tk.LEFT)

        # tag 配置（统一样式）
        self.text.tag_configure("link", underline=True)
        # 鼠标悬停和离开的光标变化
        self.text.tag_bind("link", "<Enter>", lambda e: self.text.config(cursor="hand2"))
        self.text.tag_bind("link", "<Leave>", lambda e: self.text.config(cursor=""))

    def on_get(self):
        if not self.cookie.strip():
            messagebox.showwarning("缺失 Cookie", "请先配置Cookie")
            return

        try:
            # 调用逻辑函数（保持与命令行 main 的行为一致）
            output = fetch_bili(self.cookie, write_to_file=False)
        except Exception as e:
            messagebox.showerror("请求失败", str(e))
            return

        # 显示为 JSON 格式
        pretty = json.dumps(output, ensure_ascii=False, indent=4)
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", pretty)

        # 为每个 entry 的 uri 加上 link tag（可点击）
        # 我们在插入的 JSON 文本中查找每个 uri 字符串的位置并打 tag
        for entry in output:
            uri = entry.get("uri") or ""
            if not uri:
                continue
            # 精确查找该 uri 在 pretty 文本中的位置（可能重复，但通常不同）
            # 为避免匹配到其它字段意外重复，先尝试匹配 "uri": "the_uri"
            search_pattern = f'"uri": "{uri}"'
            idx = pretty.find(search_pattern)
            if idx == -1:
                # 如果没找到，尝试仅匹配 uri 字符串
                idx = pretty.find(uri)
            if idx == -1:
                continue
            # 找到 uri 在字符串中的开始位置（uri 的字符开始）
            uri_start_in_pretty = pretty.find(uri, idx)
            uri_end_in_pretty = uri_start_in_pretty + len(uri)
            # 转换为 Text 索引
            start_index = f"1.0+{uri_start_in_pretty}c"
            end_index = f"1.0+{uri_end_in_pretty}c"

            # 为这段文本创建唯一 tag（用相同 "link" tag 处理）
            # 绑定单击事件，打开浏览器到完整 URL
            full = make_full_url(uri)
            # 使用 lambda 默认参数来捕获 full
            def open_url(event, url=full):
                if url:
                    webbrowser.open(url)

            # 添加 tag 并绑定点击事件（注意：多次绑定会覆盖同名事件，所以我们动态生成绑定）
            # 为避免重复绑定同 tag 的 click handler，我们先用独立 tag 名称
            unique_tag = f"link_{uri_start_in_pretty}"
            self.text.tag_add(unique_tag, start_index, end_index)
            self.text.tag_configure(unique_tag, underline=True, foreground="blue")
            self.text.tag_bind(unique_tag, "<Button-1>", open_url)
            self.text.tag_bind(unique_tag, "<Enter>", lambda e: self.text.config(cursor="hand2"))
            self.text.tag_bind(unique_tag, "<Leave>", lambda e: self.text.config(cursor=""))

        self.text.config(state=tk.DISABLED)

    def on_config_cookie(self):
        # 新窗口配置 Cookie
        win = tk.Toplevel(self.root)
        win.title("配置 Cookie")
        win.geometry("350x400")

        lbl = tk.Label(win, text="配置Cookie")
        lbl.pack(anchor="w", padx=8, pady=(8,0))

        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, width=80, height=12)
        txt.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)
        # 预填充已有 cookie（如果有）
        if self.cookie:
            txt.insert("1.0", self.cookie)

        def on_confirm():
            value = txt.get("1.0", tk.END).strip()
            self.cookie = value
            messagebox.showinfo("配置成功", "Cookie 已保存。")
            win.destroy()

        btn = tk.Button(win, text="确认", width=12, command=on_confirm)
        btn.pack(padx=8, pady=(0,8), anchor="e")

def run_gui():
    root = tk.Tk()
    app = BiliGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()

import json
import tkinter as tk
from tkinter import ttk, messagebox
import db_util as db


class ScrollableFrame(ttk.Frame):
    """可滚动的容器，用于承载大量行组件（Windows 鼠标滚轮行为已优化）"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.inner = ttk.Frame(self.canvas)
        self.inner.bind("<Configure>", self._on_frame_configure)

        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Windows: 仅当鼠标进入左侧列表区域（canvas）时，才绑定滚轮；离开时解除绑定
        self.canvas.bind("<Enter>", self._bind_mousewheel_win)
        self.canvas.bind("<Leave>", self._unbind_mousewheel_win)

    def _on_frame_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # 让内部框宽度自适应画布宽度
        self.canvas.itemconfig(self._win, width=event.width)

    # Windows 专用滚轮绑定（仅在鼠标进入本区域时生效）
    def _bind_mousewheel_win(self, _event=None):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_win)

    def _unbind_mousewheel_win(self, _event=None):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel_win(self, event):
        # Windows: event.delta 是 120 的倍数，向上为正
        delta = int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(delta, "units")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("prompt_generator")
        self.geometry("1000x600")
        self.minsize(900, 520)

        # 水平分割左右区域（左侧:右侧 ≈ 2:1）
        self.paned = ttk.Panedwindow(self, orient="horizontal")
        self.paned.pack(fill="both", expand=True)

        # 左右容器
        self.left = ttk.Frame(self.paned)
        self.right = ttk.Frame(self.paned)

        # 使用 weight 控制比例
        self.paned.add(self.left, weight=2)
        self.paned.add(self.right, weight=1)

        self._build_left()
        self._build_right()

        # 初始时将分割条设置在窗口宽度的 2/3 处，确保初始就是 2:1
        self.after(100, self._set_initial_sash_ratio)

        # 行缓存：table_name -> IntVar
        self.row_vars = {}

    def _set_initial_sash_ratio(self):
        try:
            total = self.paned.winfo_width()
            if total <= 1:
                # 还未完成布局，稍后再试
                self.after(100, self._set_initial_sash_ratio)
                return
            pos = int(total * 2 / 3)  # 左侧 2/3，右侧 1/3
            self.paned.sashpos(0, pos)
        except Exception:
            pass

    def _build_left(self):
        # 顶部：数据库选择
        top = ttk.Frame(self.left)
        top.pack(fill="x", padx=10, pady=(10, 6))

        ttk.Label(top, text="请选择数据库").pack(side="left")

        self.db_var = tk.StringVar(value="")
        self.db_combo = ttk.Combobox(
            top,
            state="readonly",
            textvariable=self.db_var,
            values=list(db.DB_POOLS.keys())
        )
        self.db_combo.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self.db_combo.bind("<<ComboboxSelected>>", self.on_db_selected)

        # 中部：可滚动表清单
        mid = ttk.Frame(self.left)
        mid.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 列表
        self.scroll = ScrollableFrame(mid)
        self.scroll.pack(fill="both", expand=True)

        # 底部：确认按钮
        bottom = ttk.Frame(self.left)
        bottom.pack(fill="x", padx=10, pady=(0, 12))
        self.confirm_btn = ttk.Button(bottom, text="确认", command=self.on_confirm)
        self.confirm_btn.pack(side="left")

        # 状态文本
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(self.left, textvariable=self.status_var, foreground="#888")
        self.status_label.pack(fill="x", padx=10, pady=(0, 8))

    def _build_right(self):
        # 右侧文本区域
        text_frame = ttk.Frame(self.right)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.text = tk.Text(text_frame, wrap="none", undo=True)
        self.text.configure(font=("Consolas", 10))

        yscroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        xscroll = ttk.Scrollbar(text_frame, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self.text.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        # Windows: 仅在鼠标进入文本区域时绑定滚轮，确保不影响左侧列表
        self.text.bind("<Enter>", self._bind_text_mousewheel_win)
        self.text.bind("<Leave>", self._unbind_text_mousewheel_win)

    # 事件：选择数据库
    def on_db_selected(self, _event=None):
        selected = self.db_var.get().strip()
        if not selected:
            return

        # 同步写回 prompt_generator 的全局变量
        db.DB_CHOICE = selected
        db.DSN = db.DB_POOLS.get(selected)
        db.USER = selected
        db.PASSWORD = selected

        # 加载该库的所有表
        self.load_tables()

    def clear_table_rows(self):
        for child in self.scroll.inner.winfo_children():
            child.destroy()
        self.row_vars.clear()

    def load_tables(self):
        self.clear_table_rows()
        self.status_var.set("正在加载表清单...")
        self.update_idletasks()

        try:
            tables = db.query_all_tables()  # {table_name: comment}
        except Exception as e:
            messagebox.showerror("错误", f"加载表清单失败：\n{e}")
            self.status_var.set("加载失败")
            return

        # 将表名排序，便于查找
        items = sorted(tables.items(), key=lambda kv: kv[0])

        # 构建每行
        for r, (tn, comment) in enumerate(items):
            var = tk.IntVar(value=0)
            self.row_vars[tn] = var

            # 复选框
            chk = ttk.Checkbutton(self.scroll.inner, variable=var,
                                  command=lambda t=tn, v=var: self.on_table_checked(t, v))
            chk.grid(row=r, column=0, padx=(4, 6), pady=4, sticky="w")

            # 表名
            lbl_name = ttk.Label(self.scroll.inner, text=tn, anchor="w")
            lbl_name.grid(row=r, column=1, sticky="w")

            # 注释（中文名）
            lbl_comment = ttk.Label(self.scroll.inner, text=comment or "", anchor="w")
            lbl_comment.grid(row=r, column=2, sticky="w", padx=(12, 12))

            # 查看按钮
            btn_view = ttk.Button(self.scroll.inner, text="查看",
                                  command=lambda t=tn: self.on_view_table(t))
            btn_view.grid(row=r, column=3, padx=(4, 6))

        # 列伸展
        self.scroll.inner.grid_columnconfigure(2, weight=1)

        self.status_var.set(f"共加载 {len(items)} 张表")

    # 事件：勾选表时，添加 JSON 到 TABLES 列表
    def on_table_checked(self, table_name: str, var: tk.IntVar):
        try:
            json_str = db.get_table_structure(table_name)
            if var.get() == 1:
                if json_str not in db.TABLES:
                    db.TABLES.append(json_str)
            if var.get() == 0:
                db.TABLES.remove(json_str)
        except Exception as e:
            # 出错则回退勾选状态
            var.set(0)
            messagebox.showerror("错误", f"获取表结构失败：\n{table_name}\n\n{e}")

    # 事件：查看某表结构，右侧文本区显示格式化 JSON
    def on_view_table(self, table_name: str):
        try:
            raw = db.get_table_structure(table_name)
            try:
                obj = json.loads(raw)
                pretty = json.dumps(obj, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                pretty = raw

            self.text.configure(state="normal")
            self.text.delete("1.0", "end")
            self.text.insert("1.0", pretty)
            self.text.mark_set("insert", "1.0")
            self.text.see("1.0")
        except Exception as e:
            messagebox.showerror("错误", f"查看表结构失败：\n{table_name}\n\n{e}")

    # 事件：确认 -> 跳转到新窗口
    def on_confirm(self):
        # 避免左侧列表对全局滚轮的绑定影响新窗口
        try:
            self.scroll._unbind_mousewheel_win()
        except Exception:
            pass

        win = tk.Toplevel(self)
        win.title("prompt_generator")
        win.geometry("1000x600")

        # 关闭新窗口时，退出整个应用
        def on_close():
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", on_close)

        # 容器布局：上文本区（权重1）、按钮区（权重0）、下文本区（权重1）
        container = ttk.Frame(win)
        container.pack(fill="both", expand=True)

        # 上方输入文本区
        top_frame = ttk.Frame(container)
        top_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        input_text = tk.Text(top_frame, wrap="word", undo=True, font=("Consolas", 10))
        y1 = ttk.Scrollbar(top_frame, orient="vertical", command=input_text.yview)
        input_text.configure(yscrollcommand=y1.set)
        input_text.grid(row=0, column=0, sticky="nsew")
        y1.grid(row=0, column=1, sticky="ns")
        top_frame.rowconfigure(0, weight=1)
        top_frame.columnconfigure(0, weight=1)

        # 鼠标滚轮仅滚动当前文本框
        def bind_text_mousewheel(widget):
            def _mw(event, w=widget):
                w.yview_scroll(int(-1 * (event.delta / 120)), "units")
                return "break"
            widget.bind("<MouseWheel>", _mw)

        bind_text_mousewheel(input_text)

        # 中间按钮
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        gen_btn = ttk.Button(btn_frame, text="生成")
        gen_btn.pack()

        # 下方输出文本区
        bottom_frame = ttk.Frame(container)
        bottom_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        output_text = tk.Text(bottom_frame, wrap="word", undo=True, font=("Consolas", 10))
        y2 = ttk.Scrollbar(bottom_frame, orient="vertical", command=output_text.yview)
        output_text.configure(yscrollcommand=y2.set)
        output_text.grid(row=0, column=0, sticky="nsew")
        y2.grid(row=0, column=1, sticky="ns")
        bottom_frame.rowconfigure(0, weight=1)
        bottom_frame.columnconfigure(0, weight=1)

        bind_text_mousewheel(output_text)

        container.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=0)
        container.rowconfigure(2, weight=1)
        container.columnconfigure(0, weight=1)

        # 点击“生成”的处理逻辑
        def on_generate():
            user_input = input_text.get("1.0", "end-1c")
            tables_str = "\n".join(db.TABLES)
            # 按要求拼接字符串
            result = f"{tables_str}\n请参考以上数据库表结构的json描述，实现一段sql语句：{user_input}"

            output_text.configure(state="normal")
            output_text.delete("1.0", "end")
            output_text.insert("1.0", result)
            output_text.see("1.0")

        gen_btn.config(command=on_generate)
        
    # Windows: 文本区滚轮绑定（进入时绑定，离开时解绑），并确保不影响左侧列表
    def _bind_text_mousewheel_win(self, _event=None):
        # 进入文本区时，确保左侧列表不再截获滚轮
        try:
            self.scroll._unbind_mousewheel_win()
        except Exception:
            pass
        self.text.bind("<MouseWheel>", self._on_text_mousewheel_win)

    def _unbind_text_mousewheel_win(self, _event=None):
        self.text.unbind("<MouseWheel>")

    def _on_text_mousewheel_win(self, event):
        self.text.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"  # 阻止进一步冒泡


if __name__ == "__main__":
    app = App()
    app.mainloop()

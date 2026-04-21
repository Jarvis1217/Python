import json
import os
import re
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict, List, Optional

SAVE_PATH = r"C:\Users\Jerry\AppData\Roaming\SlayTheSpire2\steam\76561198828316918\profile1\saves\current_run.save"


class SaveFileError(Exception):
    pass


class SaveEditorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Slay the Spire 2 存档编辑器")
        self.root.geometry("920x680")
        self.root.minsize(920, 680)

        self.save_path = SAVE_PATH
        self.save_data: Optional[Dict[str, Any]] = None
        self.player: Optional[Dict[str, Any]] = None
        self.original_text: Optional[str] = None
        self.indent_style: str = "  "
        self.newline_style: str = "\n"
        self.keep_trailing_newline: bool = True

        self.current_hp_var = tk.StringVar()
        self.max_hp_var = tk.StringVar()
        self.gold_var = tk.StringVar()
        self.max_energy_var = tk.StringVar()
        self.status_var = tk.StringVar(value="正在检查存档文件...")

        self._build_style()
        self._build_ui()
        self._load_save_file()

    def _build_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.root.configure(bg="#f4f6fb")
        style.configure("App.TFrame", background="#f4f6fb")
        style.configure("Card.TFrame", background="#ffffff", relief="flat")
        style.configure(
            "Header.TLabel",
            background="#f4f6fb",
            foreground="#1f2a44",
            font=("Microsoft YaHei UI", 20, "bold"),
        )
        style.configure(
            "SubHeader.TLabel",
            background="#f4f6fb",
            foreground="#5b6478",
            font=("Microsoft YaHei UI", 10),
        )
        style.configure(
            "CardTitle.TLabel",
            background="#ffffff",
            foreground="#22304d",
            font=("Microsoft YaHei UI", 12, "bold"),
        )
        style.configure(
            "Field.TLabel",
            background="#ffffff",
            foreground="#344054",
            font=("Microsoft YaHei UI", 10),
        )
        style.configure(
            "Status.TLabel",
            background="#f4f6fb",
            foreground="#475467",
            font=("Microsoft YaHei UI", 10),
        )
        style.configure(
            "Primary.TButton",
            font=("Microsoft YaHei UI", 10, "bold"),
            padding=(14, 8),
        )
        style.configure(
            "Secondary.TButton",
            font=("Microsoft YaHei UI", 10),
            padding=(12, 8),
        )

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, style="App.TFrame", padding=18)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(2, weight=1)

        header = ttk.Frame(outer, style="App.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Slay the Spire 2 存档编辑器",
            style="Header.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            header,
            text="读取并编辑 current_run.save 中第一个玩家的基础属性、卡组与遗物，卡组/遗物按原始 JSON 对象格式展示。",
            style="SubHeader.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        status_row = ttk.Frame(outer, style="App.TFrame")
        status_row.grid(row=1, column=0, sticky="ew", pady=(14, 12))
        status_row.columnconfigure(0, weight=1)

        ttk.Label(
            status_row,
            textvariable=self.status_var,
            style="Status.TLabel",
        ).grid(row=0, column=0, sticky="w")

        content = ttk.Frame(outer, style="App.TFrame")
        content.grid(row=2, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)
        content.rowconfigure(2, weight=1)

        stats_card = ttk.Frame(content, style="Card.TFrame", padding=16)
        stats_card.grid(row=0, column=0, sticky="ew")
        for i in range(4):
            stats_card.columnconfigure(i, weight=1)

        ttk.Label(
            stats_card,
            text="基础属性",
            style="CardTitle.TLabel",
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

        self._make_labeled_entry(stats_card, "当前生命", self.current_hp_var, 1, 0)
        self._make_labeled_entry(stats_card, "最大生命", self.max_hp_var, 1, 1)
        self._make_labeled_entry(stats_card, "金币", self.gold_var, 1, 2)
        self._make_labeled_entry(stats_card, "最大能量", self.max_energy_var, 1, 3)

        list_area = ttk.Frame(content, style="App.TFrame")
        list_area.grid(row=1, column=0, rowspan=2, sticky="nsew", pady=(12, 0))
        list_area.columnconfigure(0, weight=1)
        list_area.columnconfigure(1, weight=1)
        list_area.rowconfigure(0, weight=1)

        deck_card = ttk.Frame(list_area, style="Card.TFrame", padding=16)
        deck_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        deck_card.columnconfigure(0, weight=1)
        deck_card.rowconfigure(1, weight=1)
        ttk.Label(
            deck_card,
            text="卡组（原始 JSON，对象数组）",
            style="CardTitle.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.deck_text = self._make_text_widget(deck_card)
        self.deck_text.grid(row=1, column=0, sticky="nsew")

        relic_card = ttk.Frame(list_area, style="Card.TFrame", padding=16)
        relic_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        relic_card.columnconfigure(0, weight=1)
        relic_card.rowconfigure(1, weight=1)
        ttk.Label(
            relic_card,
            text="遗物（原始 JSON，对象数组）",
            style="CardTitle.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.relic_text = self._make_text_widget(relic_card)
        self.relic_text.grid(row=1, column=0, sticky="nsew")

        button_row = ttk.Frame(outer, style="App.TFrame")
        button_row.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        button_row.columnconfigure(0, weight=1)

        self.save_button = ttk.Button(
            button_row,
            text="修改并保存后退出",
            style="Primary.TButton",
            command=self._save_and_exit,
        )
        self.save_button.grid(row=0, column=1, sticky="e")

        cancel_button = ttk.Button(
            button_row,
            text="取消",
            style="Secondary.TButton",
            command=self.root.destroy,
        )
        cancel_button.grid(row=0, column=2, sticky="e", padx=(8, 0))

    def _make_labeled_entry(
        self,
        parent: ttk.Frame,
        label: str,
        var: tk.StringVar,
        row: int,
        col: int,
    ) -> None:
        wrapper = ttk.Frame(parent, style="Card.TFrame")
        wrapper.grid(row=row, column=col, sticky="ew", padx=6, pady=4)
        wrapper.columnconfigure(0, weight=1)

        ttk.Label(wrapper, text=label, style="Field.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )

        entry = ttk.Entry(wrapper, textvariable=var, font=("Microsoft YaHei UI", 11))
        entry.grid(row=1, column=0, sticky="ew")

    def _make_text_widget(self, parent: ttk.Frame) -> tk.Text:
        text = tk.Text(
            parent,
            wrap="none",
            font=("Consolas", 11),
            undo=True,
            relief="solid",
            borderwidth=1,
            background="#fbfcfe",
            foreground="#101828",
            insertbackground="#101828",
            padx=10,
            pady=10,
        )
        y_scroll = ttk.Scrollbar(parent, orient="vertical", command=text.yview)
        x_scroll = ttk.Scrollbar(parent, orient="horizontal", command=text.xview)
        text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.grid(row=1, column=1, sticky="ns")
        x_scroll.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        return text

    def _set_editable_state(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        entry_state = "normal" if enabled else "disabled"

        for child in self.root.winfo_children():
            self._set_entry_states_recursive(child, entry_state)

        self.deck_text.configure(state=state)
        self.relic_text.configure(state=state)
        self.save_button.configure(state=entry_state)

    def _set_entry_states_recursive(self, widget: tk.Widget, state: str) -> None:
        if isinstance(widget, ttk.Entry) or isinstance(widget, ttk.Button):
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass
        for child in widget.winfo_children():
            self._set_entry_states_recursive(child, state)

    def _load_save_file(self) -> None:
        if not os.path.isfile(self.save_path):
            self.status_var.set(f"未找到存档文件：{self.save_path}")
            self._clear_fields()
            self._set_editable_state(False)
            return

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                self.original_text = f.read()

            self._detect_json_style(self.original_text)
            self.save_data = json.loads(self.original_text)
            self.player = self._extract_first_player(self.save_data)
            self._populate_fields(self.player)
            self.status_var.set(f"已加载存档：{self.save_path}")
            self._set_editable_state(True)
        except Exception as exc:
            self._clear_fields()
            self._set_editable_state(False)
            self.status_var.set("存档加载失败")
            messagebox.showerror("读取失败", f"无法读取或解析存档文件：\n{exc}")

    def _detect_json_style(self, text: str) -> None:
        self.newline_style = "\r\n" if "\r\n" in text else "\n"
        self.keep_trailing_newline = text.endswith("\n") or text.endswith("\r\n")

        indent_match = re.search(r'^(?P<indent>[ \t]+)"[^"\\]+":', text, re.MULTILINE)
        if indent_match:
            self.indent_style = indent_match.group("indent")
        else:
            self.indent_style = "  "

    def _extract_first_player(self, data: Dict[str, Any]) -> Dict[str, Any]:
        players = data.get("players")
        if not isinstance(players, list) or not players:
            raise SaveFileError("存档中不存在 players 列表，或列表为空。")
        first = players[0]
        if not isinstance(first, dict):
            raise SaveFileError("players[0] 不是有效对象。")
        return first

    def _populate_fields(self, player: Dict[str, Any]) -> None:
        self.current_hp_var.set(self._safe_int_to_str(player.get("current_hp")))
        self.max_hp_var.set(self._safe_int_to_str(player.get("max_hp")))
        self.gold_var.set(self._safe_int_to_str(player.get("gold")))
        self.max_energy_var.set(self._safe_int_to_str(player.get("max_energy")))

        deck_text = self._serialize_subtree(player.get("deck", []))
        relic_text = self._serialize_subtree(player.get("relics", []))

        self.deck_text.delete("1.0", tk.END)
        self.deck_text.insert("1.0", deck_text)
        self.relic_text.delete("1.0", tk.END)
        self.relic_text.insert("1.0", relic_text)

    def _clear_fields(self) -> None:
        self.current_hp_var.set("")
        self.max_hp_var.set("")
        self.gold_var.set("")
        self.max_energy_var.set("")
        self.deck_text.delete("1.0", tk.END)
        self.relic_text.delete("1.0", tk.END)

    @staticmethod
    def _safe_int_to_str(value: Any) -> str:
        return str(value) if isinstance(value, int) else ""

    def _serialize_subtree(self, value: Any) -> str:
        indent = "\t" if self.indent_style == "\t" else len(self.indent_style)
        return json.dumps(value, ensure_ascii=False, indent=indent)

    def _parse_non_negative_int(self, name: str, value: str) -> int:
        text = value.strip()
        if text == "":
            raise SaveFileError(f"{name} 不能为空。")
        try:
            number = int(text)
        except ValueError as exc:
            raise SaveFileError(f"{name} 必须是整数。") from exc
        if number < 0:
            raise SaveFileError(f"{name} 不能为负数。")
        return number

    def _parse_object_list(self, raw_text: str, field_name: str) -> List[Dict[str, Any]]:
        text = raw_text.strip()
        if text == "":
            raise SaveFileError(f"{field_name} 不能为空。")

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SaveFileError(
                f"{field_name} 不是有效的 JSON：第 {exc.lineno} 行，第 {exc.colno} 列附近有语法错误。"
            ) from exc

        if not isinstance(parsed, list):
            raise SaveFileError(f"{field_name} 必须是 JSON 数组。")

        result: List[Dict[str, Any]] = []
        for index, item in enumerate(parsed, start=1):
            if not isinstance(item, dict):
                raise SaveFileError(f"{field_name} 第 {index} 项必须是 JSON 对象。")
            if not isinstance(item.get("id"), str) or not item.get("id"):
                raise SaveFileError(f"{field_name} 第 {index} 项缺少有效的 id 字段。")
            result.append(item)

        return result

    def _save_and_exit(self) -> None:
        if self.save_data is None or self.player is None:
            messagebox.showwarning("无法保存", "当前没有可编辑的存档数据。")
            return

        try:
            current_hp = self._parse_non_negative_int("当前生命", self.current_hp_var.get())
            max_hp = self._parse_non_negative_int("最大生命", self.max_hp_var.get())
            gold = self._parse_non_negative_int("金币", self.gold_var.get())
            max_energy = self._parse_non_negative_int("最大能量", self.max_energy_var.get())

            if current_hp > max_hp:
                raise SaveFileError("当前生命不能大于最大生命。")
            if max_energy <= 0:
                raise SaveFileError("最大能量必须大于 0。")

            deck_items = self._parse_object_list(self.deck_text.get("1.0", tk.END), "卡组")
            relic_items = self._parse_object_list(self.relic_text.get("1.0", tk.END), "遗物")

            if not deck_items:
                raise SaveFileError("卡组不能为空。")

            updated_player = dict(self.player)
            updated_player["current_hp"] = current_hp
            updated_player["max_hp"] = max_hp
            updated_player["gold"] = gold
            updated_player["max_energy"] = max_energy
            updated_player["deck"] = deck_items
            updated_player["relics"] = relic_items

            players = self.save_data.get("players")
            if not isinstance(players, list) or not players:
                raise SaveFileError("保存失败：原始存档缺少有效的 players 列表。")

            players[0] = updated_player
            self.save_data["players"] = players

            self._atomic_write_json(self.save_path, self.save_data)
            messagebox.showinfo("保存成功", "修改已写入 current_run.save，程序即将退出。")
            self.root.destroy()
        except Exception as exc:
            messagebox.showerror("保存失败", str(exc))

    def _serialize_json_preserving_style(self, data: Dict[str, Any]) -> str:
        indent = self.indent_style
        if indent == "\t":
            serialized = json.dumps(data, ensure_ascii=False, indent="\t")
        else:
            serialized = json.dumps(data, ensure_ascii=False, indent=len(indent))

        if self.newline_style != "\n":
            serialized = serialized.replace("\n", self.newline_style)

        if self.keep_trailing_newline:
            serialized += self.newline_style

        return serialized

    def _atomic_write_json(self, path: str, data: Dict[str, Any]) -> None:
        dir_name = os.path.dirname(path)
        if not os.path.isdir(dir_name):
            raise SaveFileError(f"目标目录不存在：{dir_name}")

        fd = None
        tmp_path = None
        try:
            serialized = self._serialize_json_preserving_style(data)
            fd, tmp_path = tempfile.mkstemp(
                prefix="current_run_",
                suffix=".tmp",
                dir=dir_name,
                text=True,
            )
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as tmp_file:
                fd = None
                tmp_file.write(serialized)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
            os.replace(tmp_path, path)
        except Exception as exc:
            raise SaveFileError(f"写入存档文件失败：{exc}") from exc
        finally:
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass


def main() -> None:
    root = tk.Tk()
    app = SaveEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        try:
            messagebox.showerror("程序错误", f"程序启动失败：\n{exc}")
        except Exception:
            pass
        raise

import tkinter as tk
from openai import OpenAI
import threading
import queue

client = OpenAI(api_key="<API-Key>", base_url="https://api.deepseek.com")
messages = [{"role": "system", "content": ""}]

message_queue = queue.Queue()
stop_thread = threading.Event()

# 创建主窗口
root = tk.Tk()
root.title("LLM_GUI")
root.geometry("500x500")
# 展示对话记录
top_frame = tk.Frame(root)
top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

message_display = tk.Text(top_frame, wrap=tk.WORD, state=tk.DISABLED)
message_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

message_display.tag_configure('user', justify=tk.RIGHT)
message_display.tag_configure('ai', background="gray", foreground="white")

scrollbar = tk.Scrollbar(top_frame, command=message_display.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
message_display.config(yscrollcommand=scrollbar.set)

# 用户消息输入
bottom_frame = tk.Frame(root)
bottom_frame.pack(fill=tk.X, padx=10, pady=10)

user_input = tk.Text(bottom_frame, height=8)
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)

# 插入提示词模板
prompt_template = """
角色：你是专业的提示词工程师。
任务：根据以下描述，生成一个优化的提示词，以确保大语言模型提供准确和详细的回答。
描述：
"""
user_input.insert("1.0", prompt_template.strip())

# 更新文本框
def update_text_widget():
    try:
        # 使用non-block方式检查队列
        message = message_queue.get_nowait()
        if message is None:
            message_display.insert(tk.END, "\n", "ai")
            message_display.insert(tk.END, "\n", "ai")
            message_display.config(state=tk.DISABLED)
            return
        message_display.config(state=tk.NORMAL)
        message_display.insert(tk.END, message, "ai")
        root.after(100, update_text_widget)
    except queue.Empty:
        root.after(100, update_text_widget)

# 获取AI回复
def get_response(user_msg):
        global messages, message_queue

        messages.append({"role": "user", "content": user_msg})

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages = messages,
            stream = True
        )

        # 流式输出处理
        collected_messages = []
        message_queue.put("\n")
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                message_queue.put(content)
                collected_messages.append(content)

        message_queue.put(None)

        # 多轮对话
        full_response = ''.join(collected_messages)
        messages.append({"role": "assistant", "content": full_response})

# 发送消息
def send_message(event):
    user_message = user_input.get('1.0', tk.END).strip()
    if user_message != '':
        message_display.config(state=tk.NORMAL)
        message_display.insert(tk.END, "\n", "user")
        message_display.insert(tk.END, user_message + "\n\n", "user")
        message_display.see(tk.END)
        user_input.delete('1.0', tk.END)

        # AI回复
        thread = threading.Thread(target=get_response, args=(user_message,))
        thread.start()
        update_text_widget()

# 按键处理
def on_key_press(event):
    if event.keysym == 'Return':
        if event.state & 0x1: # Shift + Enter 换行
            user_input.insert(tk.INSERT, '\n')
            return "break" # 阻止默认换行
        else:
            send_message(event)
            return "break" # 阻止默认换行

user_input.bind('<KeyPress>', on_key_press)

# 选中复制
def on_select(event):
    try:
        root.clipboard_clear()
        text = message_display.get("sel.first", "sel.last")
        root.clipboard_append(text)
    except tk.TclError:
        pass

message_display.bind("<ButtonRelease-1>", on_select)

# 关闭窗口时销毁线程
def on_closing():
    stop_thread.set()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

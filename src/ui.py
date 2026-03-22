import json
import os
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, Menu
from datetime import datetime
from src.model import call_ollama_stream
from src.utils import save_chat_history, load_chat_history

# 读取配置
def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()
chat_history = []

# 发送消息 + 指令处理
def send_message():
    global chat_history
    user_input = input_box.get("1.0", tk.END).strip()
    input_box.delete("1.0", tk.END)
    
    if not user_input:
        return

    # 指令系统
    chat_box.config(state=tk.NORMAL)
    if user_input.lower() == "quit":
        chat_box.insert(tk.END, "AI：再见！祝你有美好的一天~✨\n\n", "ai")
        chat_box.config(state=tk.DISABLED)
        chat_box.update()
        root.after(1000, root.destroy)
        return
    elif user_input.lower() == "clear":
        chat_box.delete("1.0", tk.END)
        chat_history = []
        chat_box.insert(tk.END, "✅ 已清空所有聊天记录\n\n", "ai")
        chat_box.config(state=tk.DISABLED)
        return
    elif user_input.lower() == "history":
        chat_box.insert(tk.END, "📜 最近聊天记录：\n", "ai")
        for item in chat_history[-10:]:
            chat_box.insert(tk.END, f"[{item['time']}] 你：{item['user']}\n", "user")
            chat_box.insert(tk.END, f"[{item['time']}] AI：{item['ai']}\n", "ai")
        chat_box.insert(tk.END, "\n")
        chat_box.config(state=tk.DISABLED)
        return
    elif user_input.lower() == "load":
        chat_history = load_chat_history()
        chat_box.insert(tk.END, f"✅ 已加载历史记录，共 {len(chat_history)} 条\n\n", "ai")
        chat_box.config(state=tk.DISABLED)
        return
    elif user_input.lower() == "save":
        save_chat_history(chat_history)
        chat_box.insert(tk.END, "✅ 对话已保存到 logs/chat_history.json\n\n", "ai")
        chat_box.config(state=tk.DISABLED)
        return
    elif user_input.startswith("model "):
        new_model = user_input.split(" ", 1)[1]
        config["model"] = new_model
        chat_box.insert(tk.END, f"✅ 已切换模型为：{new_model}\n\n", "ai")
        chat_box.config(state=tk.DISABLED)
        return

    # 显示用户消息
    chat_box.insert(tk.END, f"你：{user_input}\n", "user")
    chat_box.config(state=tk.DISABLED)
    chat_box.update()
    
    # 生成提示词
    history_prompt = ""
    for item in chat_history[-config["max_history"]:]:
        history_prompt += f"用户：{item['user']}\nAI：{item['ai']}\n"
    
    prompt = f"""
当前时间：{datetime.now().strftime("%Y年%m月%d日")}
历史对话：
{history_prompt}
用户：{user_input}

请用友好、温暖、有人情味的语气回答，趣味问题可以轻松幽默，像朋友聊天一样。
请直接用中文回答，不要输出多余内容。
AI:
"""
    
    # AI回复
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, "AI：", "ai")
    full_reply = ""
    try:
        for chunk in call_ollama_stream(prompt, config):
            full_reply += chunk
            chat_box.insert(tk.END, chunk, "ai")
            chat_box.update()
    except Exception as e:
        chat_box.insert(tk.END, f"出错啦：{str(e)}", "ai")
    
    # 保存对话
    chat_history.append({
        "time": datetime.now().strftime("%H:%M"),
        "user": user_input,
        "ai": full_reply
    })
    if len(chat_history) > config["max_history"]:
        chat_history.pop(0)
    save_chat_history(chat_history)
    
    chat_box.insert(tk.END, "\n\n")
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)

# 创建主窗口
root = tk.Tk()
root.title("离线AI助手 - 图形版")
root.geometry("700x600")
root.resizable(False, False)

# 顶部帮助菜单
menubar = Menu(root)
root.config(menu=menubar)
help_menu = Menu(menubar, tearoff=0)
help_menu.add_command(
    label="指令说明",
    command=lambda: messagebox.showinfo(
        "📖 指令帮助",
        """可用指令列表：
clear：清空当前聊天记录
history：查看最近10条聊天记录
save：保存当前对话到本地
load：加载之前保存的对话记录
model 模型名：切换AI模型（例：model qwen:14b）
quit：退出程序

💡 提示：输入指令时不需要区分大小写~"""
    )
)
menubar.add_cascade(label="帮助", menu=help_menu)

# 蓝色欢迎框（统一冒号格式 + 优化文字）
welcome_text = f"""🧠 离线智能对话助手（简历版）
模型：{config["model"]} | 采样温度：{config["temperature"]} | 上下文：{config["max_history"]}条
指令：clear：清空 | history：历史记录 | save：保存 | load：加载 | model 模型名：切换 | quit：退出"""
welcome_label = tk.Label(
    root, text=welcome_text, bg="#e6f7ff", fg="#0066cc",
    font=("微软雅黑", 10), justify="left", padx=12, pady=10
)
welcome_label.pack(pady=10, padx=10, fill="x")

# 聊天框
chat_box = scrolledtext.ScrolledText(root, font=("微软雅黑", 10))
chat_box.pack(pady=5, padx=10, fill="both", expand=True)
chat_box.tag_config("user", foreground="blue")
chat_box.tag_config("ai", foreground="green")
chat_box.config(state=tk.DISABLED)

# 输入区域
frame = tk.Frame(root)
frame.pack(pady=10, padx=10, fill="x")
input_box = scrolledtext.ScrolledText(frame, height=3, font=("微软雅黑", 11))
input_box.pack(side=tk.LEFT, padx=8, fill="x", expand=True)
send_btn = ttk.Button(frame, text="发送", command=send_message, width=8)
send_btn.pack(side=tk.RIGHT, padx=8)

if __name__ == "__main__":
    root.mainloop()
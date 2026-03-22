import json
import os
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, Menu
from datetime import datetime

# ===================== 工具函数 =====================
def save_chat_history(history):
    try:
        if not os.path.exists("logs"):
            os.makedirs("logs")
        with open("logs/chat_history.json", "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("保存失败", f"聊天记录保存失败：{str(e)}")

def load_chat_history():
    try:
        with open("logs/chat_history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        messagebox.showerror("加载失败", f"历史记录加载失败：{str(e)}")
        return []

# ===================== 模型调用 =====================
def call_ollama_stream(prompt, config):
    try:
        import requests
        url = "http://localhost:11434/api/generate"
        payload = {"model": config["model"], "prompt": prompt, "stream": True}
        response = requests.post(url, json=payload, stream=True, timeout=10)
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]
    except Exception as e:
        raise Exception(f"模型调用失败：{str(e)}\n请检查 Ollama 是否启动！")

# ===================== 配置加载 =====================
def load_config():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("配置错误", f"配置文件加载失败：{str(e)}")
        return {"model": "qwen:14b", "temperature": 0.3, "max_history": 10}

config = load_config()
chat_history = []

# ===================== 输入框提示 =====================
def add_placeholder():
    input_box.delete("1.0", tk.END)
    input_box.insert("1.0", "输入消息...")
    input_box.config(fg="gray")

def on_focus_in(event):
    if input_box.get("1.0", "end-1c") == "输入消息...":
        input_box.delete("1.0", tk.END)
        input_box.config(fg="black")

def on_focus_out(event):
    if input_box.get("1.0", "end-1c").strip() == "":
        add_placeholder()

# ===================== 🔥 终极修复：换行永不丢失 =====================
def send_message():
    global chat_history
    send_btn.config(state=tk.DISABLED)
    
    user_input = input_box.get("1.0", "end-1c").strip()
    if user_input == "输入消息..." or user_input == "":
        add_placeholder()
        send_btn.config(state=tk.NORMAL)
        return

    input_box.delete("1.0", tk.END)
    chat_box.config(state=tk.NORMAL)

    # 1. 用户消息（末尾加换行）
    chat_box.insert(tk.END, f"你：{user_input}\n", "user")
    # 2. 思考提示（单独一行）
    chat_box.insert(tk.END, "AI：正在思考中，请稍候...", "ai")
    chat_box.config(state=tk.DISABLED)
    chat_box.update()
    root.update()

    try:
        if user_input.lower() == "quit":
            chat_box.config(state=tk.NORMAL)
            chat_box.delete("end-1l linestart", tk.END)
            chat_box.insert(tk.END, "AI：再见！祝你有美好的一天~✨\n", "ai")
            chat_box.config(state=tk.DISABLED)
            root.after(1000, root.destroy)
            return
        elif user_input.lower() == "clear":
            chat_box.config(state=tk.NORMAL)
            chat_box.delete("1.0", tk.END)
            chat_history = []
            chat_box.insert(tk.END, "✅ 已清空所有聊天记录\n\n", "ai")
        elif user_input.lower() == "history":
            chat_box.config(state=tk.NORMAL)
            chat_box.delete("end-1l linestart", tk.END)
            chat_box.insert(tk.END, "📜 最近聊天记录：\n", "ai")
            for item in chat_history[-10:]:
                chat_box.insert(tk.END, f"[{item['time']}] 你：{item['user']}\n", "user")
                chat_box.insert(tk.END, f"[{item['time']}] AI：{item['ai']}\n", "ai")
            chat_box.insert(tk.END, "\n")
        elif user_input.lower() == "load":
            chat_history = load_chat_history()
            chat_box.config(state=tk.NORMAL)
            chat_box.delete("end-1l linestart", tk.END)
            chat_box.insert(tk.END, f"✅ 已加载历史记录，共 {len(chat_history)} 条\n\n", "ai")
        elif user_input.lower() == "save":
            save_chat_history(chat_history)
            chat_box.config(state=tk.NORMAL)
            chat_box.delete("end-1l linestart", tk.END)
            chat_box.insert(tk.END, "✅ 对话已保存到 logs/chat_history.json\n\n", "ai")
        elif user_input.startswith("model "):
            config["model"] = user_input.split(" ", 1)[1]
            chat_box.config(state=tk.NORMAL)
            chat_box.delete("end-1l linestart", tk.END)
            chat_box.insert(tk.END, f"✅ 已切换模型为：{config['model']}\n\n", "ai")
        else:
            history_prompt = ""
            for item in chat_history[-config["max_history"]:]:
                history_prompt += f"用户：{item['user']}\nAI：{item['ai']}\n"

            prompt = f"""
当前时间：{datetime.now().strftime("%Y-%m-%d")}
历史对话：
{history_prompt}
用户：{user_input}

规则：
1. 同语言回复
2. 纠正错别字
3. 准确不编造
4. 语气自然

直接回答：
"""
            full_reply = ""
            chat_box.config(state=tk.NORMAL)
            
            # 🔥 关键：先删除思考提示，再强制换行
            chat_box.delete("end-1l linestart", tk.END)
            # 🔥 强制插入换行 + AI，保证回答在新行
            chat_box.insert(tk.END, "\nAI：", "ai")
            
            for chunk in call_ollama_stream(prompt, config):
                full_reply += chunk
                chat_box.insert(tk.END, chunk, "ai")
                chat_box.update()
            
            # 🔥 AI回答后再补一个换行，彻底和下一条消息分开
            chat_box.insert(tk.END, "\n", "ai")
            
            chat_history.append({
                "time": datetime.now().strftime("%H:%M"),
                "user": user_input,
                "ai": full_reply
            })

        chat_box.config(state=tk.DISABLED)
        chat_box.see(tk.END)

    except Exception as e:
        chat_box.config(state=tk.NORMAL)
        chat_box.delete("end-1l linestart", tk.END)
        chat_box.insert(tk.END, "\nAI：抱歉，暂时无法回复你~😔\n", "ai")
        chat_box.config(state=tk.DISABLED)
        messagebox.showerror("程序异常", f"运行出错：{str(e)}")
    
    finally:
        send_btn.config(state=tk.NORMAL)
        add_placeholder()

# ===================== 界面（100%还原） =====================
root = tk.Tk()
root.title("离线AI助手 - 图形版1.0")
root.geometry("750x650")
root.resizable(False, False)

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
model 模型名：切换AI模型
quit：退出程序

💡 提示：输入指令时不需要区分大小写~"""
    )
)
menubar.add_cascade(label="帮助", menu=help_menu)

welcome_text = f"""🧠 离线智能对话助手 1.0
模型：{config["model"]} | 采样温度: 0.3 | 上下文: 10条
指令：clear：清空 | history：历史记录 | save：保存 | load：加载 | model 模型名：切换 | quit：退出"""
welcome_label = tk.Label(
    root, text=welcome_text, bg="#e6f7ff", fg="#0066cc",
    font=("微软雅黑", 10), justify="left", padx=12, pady=10
)
welcome_label.pack(pady=10, padx=10, fill="x")

chat_box = scrolledtext.ScrolledText(root, font=("微软雅黑", 10), wrap=tk.WORD)
chat_box.pack(pady=5, padx=10, fill="both", expand=True)
chat_box.tag_config("user", foreground="blue")
chat_box.tag_config("ai", foreground="green")
chat_box.config(state=tk.DISABLED)

frame = tk.Frame(root)
frame.pack(pady=5, padx=10, fill="x")
input_box = scrolledtext.ScrolledText(frame, height=3, font=("微软雅黑", 11))
input_box.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
send_btn = ttk.Button(frame, text="发送", command=send_message, width=8)
send_btn.grid(row=0, column=1, sticky="nsew")
frame.grid_columnconfigure(0, weight=1)

input_box.bind("<FocusIn>", on_focus_in)
input_box.bind("<FocusOut>", on_focus_out)
add_placeholder()

if __name__ == "__main__":
    root.mainloop()
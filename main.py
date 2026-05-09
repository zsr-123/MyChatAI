import json
import os
import sys
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

# ===================== 🤖 AI Agent 工具库 =====================
def get_real_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def count_chat_total(history):
    return f"当前总对话条数：{len(history)} 条"

def auto_save_chat(history):
    try:
        content = ""
        for item in history:
            content += f"[{item['time']}] 你：{item['user']}\n[{item['time']}] AI：{item['ai']}\n\n"
        with open("agent_chat_record.txt", "w", encoding="utf-8") as f:
            f.write(content)
        return "✅ Agent已自动保存聊天记录到 agent_chat_record.txt"
    except:
        return "❌ 保存失败"

def calculate(expr):
    try:
        clean_expr = ''.join(c for c in expr if c in '0123456789+-*/() ')
        return f"🧮 计算结果：{eval(clean_expr)}"
    except:
        return "❌ 算式错误，无法计算"

# ===================== 🧠 AI Agent 调度大脑 =====================
def agent_task(user_input, chat_history):
    text = user_input.strip().lower()
    if "现在几点" in text or "当前时间" in text or "几点了" in text:
        return f"⏰ 电脑真实时间：{get_real_time()}"
    elif "统计对话" in text or "多少条" in text:
        return count_chat_total(chat_history)
    elif "自动保存" in text or "保存聊天" in text:
        return auto_save_chat(chat_history)
    elif any(ch in text for ch in "+-*/"):
        return calculate(text)
    return None

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

# ===================== 配置加载（打包EXE兼容）=====================
def load_config():
    try:
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
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

# ===================== 发送消息（2.0知识严谨+Agent）=====================
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

    chat_box.insert(tk.END, f"你：{user_input}\n", "user")
    agent_res = agent_task(user_input, chat_history)
    if agent_res:
        chat_box.insert(tk.END, f"🤖 Agent：{agent_res}\n\n", "ai")
        chat_box.config(state=tk.DISABLED)
        chat_box.see(tk.END)
        send_btn.config(state=tk.NORMAL)
        add_placeholder()
        return

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
你是一个严谨、准确的AI助手，回答必须严格遵守以下规则：
1. 知识必须100%基于事实，不编造、不猜测、不虚构任何信息。
2. 前后回答必须完全一致，不能自相矛盾、前后改口。
3. 当用户的说法与事实不符时，礼貌纠正用户，不顺着用户的错误说法回答。
4. 回答简洁清晰，不啰嗦、不重复，不输出无关内容。
5. 严格根据用户的问题回答，不跑题，不受用户错误引导干扰。
6. 对于不确定的内容，直接说明“无法确定”，不编造信息。

当前时间：{datetime.now().strftime("%Y-%m-%d")}
历史对话：
{history_prompt}
用户：{user_input}

直接回答：
"""
            full_reply = ""
            chat_box.config(state=tk.NORMAL)
            
            chat_box.delete("end-1l linestart", tk.END)
            chat_box.insert(tk.END, "\nAI：", "ai")
            
            for chunk in call_ollama_stream(prompt, config):
                full_reply += chunk
                chat_box.insert(tk.END, chunk, "ai")
                chat_box.update()
            
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

# ===================== 界面 2.0版本 =====================
root = tk.Tk()
root.title("离线AI助手 - 图形版2.0")
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

welcome_text = f"""🧠 离线智能对话助手 2.0
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
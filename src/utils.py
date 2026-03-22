import json
import os

def save_chat_history(history):
    """保存聊天记录到 logs/chat_history.json"""
    if not os.path.exists("logs"):
        os.makedirs("logs")
    with open("logs/chat_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_chat_history():
    """从 logs/chat_history.json 加载聊天记录，不存在则返回空列表"""
    try:
        with open("logs/chat_history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
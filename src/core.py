import json
import os
from datetime import datetime

class ChatCore:
    def __init__(self, config):
        self.config = config
        self.history = []
        self.max_history = config["max_history"]
        # 确保logs目录存在
        os.makedirs("logs", exist_ok=True)

    def add_to_history(self, user_input, ai_reply):
        """添加对话到历史记录"""
        self.history.append({
            "user": user_input,
            "ai": ai_reply,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        # 超过最大长度，删除最早的一条
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_history_prompt(self):
        """生成历史对话提示词（给模型看）"""
        history_text = ""
        for item in self.history[-self.max_history:]:
            history_text += f"用户：{item['user']}\nAI：{item['ai']}\n"
        return history_text

    def handle_command(self, user_input):
        """处理系统指令（clear/history/save/load/model），返回指令结果或None（不是指令）"""
        user_input = user_input.lower().strip()
        
        if user_input == "clear":
            self.history = []
            return "✅ 已清空全部对话历史"
        elif user_input == "history":
            return self.format_history()
        elif user_input == "save":
            self.save_history()
            return "✅ 对话已保存到 logs/chat_history.json"
        elif user_input == "load":
            self.load_history()
            return "✅ 已加载历史对话"
        elif user_input.startswith("model "):
            # 切换模型，比如：model llama3:8b
            new_model = user_input.split(" ")[1]
            self.config["model"] = new_model
            return f"✅ 已切换模型为：{new_model}"
        # 不是系统指令，返回None
        return None

    def format_history(self):
        """格式化输出对话历史（给用户看）"""
        if not self.history:
            return "📜 暂无对话记录"
        text = "📜 最近对话：\n"
        for i, item in enumerate(self.history[-self.max_history:], 1):
            text += f"  {i}. [{item['time']}] 你：{item['user']}\n     AI：{item['ai']}\n"
        return text

    def save_history(self):
        """保存对话历史到JSON文件"""
        with open("logs/chat_history.json", "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def load_history(self):
        """从JSON文件加载对话历史"""
        try:
            with open("logs/chat_history.json", "r", encoding="utf-8") as f:
                self.history = json.load(f)
        except FileNotFoundError:
            self.history = []
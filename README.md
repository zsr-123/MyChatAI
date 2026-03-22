离线 AI 助手 - 图形版 1.0
基于 Ollama + Python Tkinter 开发的离线智能对话助手，无需联网即可在本地运行，支持中英文智能对话、上下文记忆、快捷指令操作。
🚀 快速开始
1. 环境准备
安装 Python 3.10+
安装并启动 Ollama 服务：Ollama 官网 下载安装，运行 ollama serve
下载默认模型：ollama pull qwen:14b（可在 config.json 中切换其他 Ollama 模型）
2. 运行程序
bash
运行
# 克隆项目
git clone https://github.com/[ZSR-123]/MyChatAI.git
cd MyChatAI

# 安装依赖
pip install -r requirements.txt

# 运行主程序
python main.py
✨ 功能特性
✅ 离线运行：基于 Ollama 本地模型，完全无需联网
✅ 图形界面：简洁直观的 Tkinter GUI，操作友好
✅ 智能对话：自动识别中英文，支持上下文记忆（最多 10 条历史）
✅ 快捷指令：内置 clear/history/save/load/model/quit 等指令
✅ 记录持久化：自动保存聊天记录到 logs/chat_history.json，支持加载历史
✅ 异常保护：程序出错不闪退，友好提示用户
📖 指令说明
表格
指令	功能描述
clear	清空当前所有聊天记录
history	查看最近 10 条聊天历史
save	保存当前对话到本地 logs/chat_history.json
load	加载之前保存的聊天记录
model 模型名	切换 Ollama 模型（例如：model qwen:7b）
quit	退出程序
👨‍💻 开发者信息
开发者：[张思睿]
GitHub：[ZSR-123]
技术栈：Python 3.x + Tkinter + Ollama API
项目版本：1.0
项目初衷：学习离线 AI 对话系统开发，实践 GUI 界面与本地模型调用
🤝 致谢与声明
本项目在 AI 辅助开发 的支持下完成，核心逻辑、界面优化与问题调试均获得技术指导与帮助。项目所有代码均为独立实现与整理，遵循开源精神分享。
📸 界面预览
![界面预览](screenshots/preview.png)
📝 更新日志
v1.0 (2026-03-22)
实现基础图形界面
支持中英文智能对话
添加上下文记忆功能
实现快捷指令操作
完善聊天记录保存与加载
优化界面显示与换行逻辑
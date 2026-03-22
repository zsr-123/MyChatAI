from transformers import pipeline, AutoTokenizer
import os

# 这里使用一个轻量级开源模型，适合新手测试
MODEL_NAME = "uer/gpt2-chinese-small"

def load_ai_model():
    print("正在加载AI模型（首次运行会自动下载，较慢）...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    # 使用pipeline快速生成文本
    generator = pipeline(
        "text-generation",
        model=MODEL_NAME,
        tokenizer=tokenizer,
        device=-1  # 强制使用CPU，如果有显卡可改为0
    )
    return generator

def main():
    print("=== 你的专属AI聊天软件 ===")
    print("输入 'quit' 退出程序\n")
    
    model = load_ai_model()
    
    while True:
        user_input = input("你: ")
        if user_input.lower() == "quit":
            print("AI: 再见！")
            break
        if not user_input:
            print("AI: 请输入内容。")
            continue
        
        # 生成回复
        print("AI: ", end="")
        result = model(
            user_input,
            max_length=100,  # 生成最大长度
            num_return_sequences=1,
            pad_token_id=tokenizer.eos_token_id
        )
        # 提取生成的文本
        print(result[0]['generated_text'].replace(user_input, "").strip())

if __name__ == "__main__":
    # 解决Windows终端编码问题
    os.system("chcp 65001")
    main()
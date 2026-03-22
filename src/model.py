import json
import requests

def call_ollama(prompt, config):
    """非流式调用：一次性返回完整回答"""
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": config["model"],
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": config["temperature"],
            "num_ctx": config["num_ctx"],
            "num_predict": config["num_predict"]
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()["response"].strip()
    except requests.exceptions.ConnectionError:
        return "❌ 错误：Ollama服务未启动，请先运行 `ollama serve`"
    except requests.exceptions.Timeout:
        return "❌ 错误：请求超时，请检查模型状态或网络"
    except Exception as e:
        return f"❌ 模型调用失败：{str(e)}"

def call_ollama_stream(prompt, config):
    """流式调用：逐字输出回答（体验更好）"""
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": config["model"],
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": config["temperature"],
            "num_ctx": config["num_ctx"],
            "num_predict": config["num_predict"]
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data, stream=True, timeout=60)
        for line in response.iter_lines():
            if line:
                yield json.loads(line)["response"]
    except requests.exceptions.ConnectionError:
        yield "❌ 错误：Ollama服务未启动，请先运行 `ollama serve`"
    except requests.exceptions.Timeout:
        yield "❌ 错误：请求超时，请检查模型状态或网络"
    except Exception as e:
        yield f"❌ 模型调用失败：{str(e)}"
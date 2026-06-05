import requests
from typing import List, Dict, Any
from app.core.config import settings

# 通用API调用函数
def call_deepseek(messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
    # 构建请求头，携带API Key
    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    # 构建请求体，指定模型deepseek-chat、消息列表、温度、非流式输出
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": temperature,
        "stream": False
    }
    # 发送 POST 请求到 DeepSeek 的 /chat/completions 端点
    response = requests.post(
        f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
        headers=headers,
        json=payload
    )
    # 如果 HTTP 状态码不是 2xx，抛出异常
    response.raise_for_status()
    # 解析 JSON 响应，提取 choices[0].message.content
    return response.json()["choices"][0]["message"]["content"]

# 智能任务拆解
def suggest_subtasks(title: str, description: str = "") -> List[str]:
    prompt = f"""你是一个项目助理。请为以下任务拆解出具体的子任务步骤（3-5条），每条用 - 开头。

任务标题：{title}
任务描述：{description or "无"}

要求：子任务应具体、可执行、按顺序排列。只输出子任务列表，不要有其他解释。"""
    response = call_deepseek([{"role": "user", "content": prompt}])
    subtasks = []
    for line in response.strip().split("\n"):
        line = line.strip()
        if line.startswith("-"):
            subtasks.append(line[1:].strip())
    return subtasks if subtasks else ["- 分析需求", "- 设计方案", "- 执行开发", "- 测试验证"]

# 生成每日工作摘要
def generate_daily_summary(user_name: str, tasks: List[Dict[str, Any]]) -> str:
    if not tasks:
        return "今日没有任务，好好休息一下吧。"
    task_list = "\n".join([f"- {t['title']} (状态: {t['status']})" for t in tasks])
    prompt = f"""你是一个工作助理。请为以下用户生成今日工作摘要，语气积极、专业。

用户：{user_name}
今日任务：
{task_list}

要求：用2-3句话总结工作进展，并给出一个简短的鼓励或建议。"""
    return call_deepseek([{"role": "user", "content": prompt}], temperature=0.5)
import re
from textwrap import dedent
from openai import OpenAI

client = OpenAI(api_key="<API-Key>", base_url="https://api.deepseek.com")
messages = [{"role": "system", "content": "用中文回答。"}]


# 优化提示词
def optimize_prompt(user_prompt):
    prompt_template = """
    角色：你是专业的提示词工程师。
    任务：根据以下描述，生成一个优化的提示词，以确保大语言模型提供准确和详细的回答。生成的提示词请用三个反引号（```）包裹。
    描述：
    """

    user_prompt = dedent(prompt_template).strip() + user_prompt
    temp_messages = [{"role": "system", "content": "用中文回答。"}, {"role": "user", "content": user_prompt}]
    response = client.chat.completions.create(model="deepseek-chat", messages=temp_messages)

    pattern = r'```.*?```'
    matches = re.findall(pattern, response.choices[0].message.content, re.DOTALL)
    matches[0].strip("```").strip()

    return matches[0].strip("```").strip()


# 获取 LLM 回复
def get_response():
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True
    )

    # 流式输出处理
    collected_messages = []
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end='', flush=True)  # 实时打印消息
            collected_messages.append(content)  # 收集完整消息

    # 多轮对话
    full_response = ''.join(collected_messages)
    messages.append({"role": "assistant", "content": full_response})


if __name__ == '__main__':
    while True:
        prompt = input(">>> ")

        if prompt == "q":
            break

        # 展示 prompt 优化结果
        prompt = optimize_prompt(prompt)
        print(f"\n[OPTIMIZED PROMPT]:\n\n{prompt}\n\n[LLM_RESPONSE]:\n")

        # 展示 LLM 回复
        messages.append({"role": "user", "content": prompt})
        get_response()
        print("\n")

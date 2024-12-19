import re
from textwrap import dedent
from openai import OpenAI

client = OpenAI(api_key="qwen", base_url="http://localhost:11434/v1/")
model = "qwen2.5:14b"
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
    response = client.chat.completions.create(model=model, messages=temp_messages)

    pattern = r'```.*?```'
    matches = re.findall(pattern, response.choices[0].message.content, re.DOTALL)

    return matches[0].strip("```").strip()


# 获取 LLM 回复
def get_response():
    response = client.chat.completions.create(
        model=model,
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


# 保存对话记录
def save_messages(file_name):
    file_name = file_name + ".md"

    md_content = ""
    for message in messages[1:]:
        role = message.get("role").capitalize()
        content = message.get("content", "")
        md_content += f"**{role}:**\n\n{content}\n\n---\n\n"

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(md_content)

    print(f'\n已保存为：{file_name} \n')


if __name__ == '__main__':
    while True:
        prompt = input("\033[32m>>>\033[0m ")

        if prompt == "exit":
            break
        if prompt == "help":
            help_prompt = """
            1.optimize {prompt} - 仅优化提示词
            1.# {prompt}        - 优化提示词后发起会话
            2.save {file_name}  - 保存对话记录为md文件
            3.help              - 帮助信息
            4.exit              - 退出
            """
            print("\n" + dedent(help_prompt).strip() + "\n")
            continue
        if prompt.startswith("save "):
            save_messages(prompt.replace("save ", ""))
            continue
        if prompt.startswith("optimize "):
            prompt = optimize_prompt(prompt.replace("optimize ", ""))
            print(f"\n\033[34m[OPTIMIZED PROMPT]:\033[0m\n\n{prompt}\n")
            continue
        if prompt.startswith("# "):
            prompt = optimize_prompt(prompt.replace("# ", ""))
            print(f"\n\033[34m[OPTIMIZED PROMPT]:\033[0m\n\n{prompt}\n\n\033[34m[LLM_RESPONSE]:\033[0m\n")
        else:
            print(f"\n\033[34m[LLM_RESPONSE]:\033[0m\n")

        messages.append({"role": "user", "content": prompt})
        get_response()
        print("\n")

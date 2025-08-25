from openai import OpenAI
from textwrap import dedent

client = OpenAI(api_key="<API_KEY>", base_url="https://api.deepseek.com")

messages = []

# 获取回复
def get_response(prompt):
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages,
        stream=True
    )

    content_buffer, thinking = [], 1
    print("<thinking>\n")

    for chunk in response:
        reasoning_content = chunk.choices[0].delta.reasoning_content
        content = chunk.choices[0].delta.content

        if reasoning_content is not None:
            print(reasoning_content.replace("\n\n", "\n"), end="", flush=True)
        else:
            if thinking == 1:
                print("\n\n</thinking>\n")
                thinking -= 1

            print(content, end="", flush=True)
            content_buffer.append(content)

    print("\n")
    messages.append({"role": "assistant", "content": "".join(content_buffer)})

# 保存记录
def save_to_md(file_name):
    with open(file_name, "w", encoding="utf-8") as md_file:
        for message in messages:
            role = message.get("role", "unknown")
            content = message.get("content", "")
            
            # 写入角色和内容
            md_file.write(f"## {role.capitalize()}\n\n")
            md_file.write(f"{content}\n\n")
            md_file.write("---\n\n")
    print(f"已保存：{file_name}\n")

if __name__ == "__main__":
    while True:
        prompt = input("> ")
        if "save" in prompt:
            file_name = prompt.split(" ")[1]
            save_to_md(file_name)
        else:
            get_response(prompt)

from openai import OpenAI
from textwrap import dedent

client = OpenAI(api_key="<API_KEY>", base_url="https://api.deepseek.com")

messages = []

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

    print()
    messages.append({"role": "assistant", "content": "".join(content_buffer)})

if __name__ == "__main__":
    prompt = """
    详细的介绍以下你自己，包括但不限于你的模型版本、知识库截止日期等。
    """
    get_response(dedent(prompt).strip())

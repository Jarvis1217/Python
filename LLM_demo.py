from openai import OpenAI

client = OpenAI(api_key="<API KEY>", base_url="https://api.deepseek.com")

messages = [{"role": "system", "content": "你是一名专业的python程序员，请用纯文本格式回答我的所有问题。"}]

while True:
    que = input(">>> ")

    if que == "q":
        break

    messages.append({"role": "user", "content": que})

    # 发起请求
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages = messages,
        stream = True
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
    print("\n")

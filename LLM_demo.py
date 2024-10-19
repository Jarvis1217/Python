from openai import OpenAI

client = OpenAI(api_key="<API KEY>", base_url="https://api.deepseek.com")

messages = [{"role": "system", "content": "你是一名专业的python程序员，请用纯文本格式回答我的所有问题。"}]

while True:
    que = input(">>> ")

    messages.append({"role": "user", "content": que})

    # 发起请求
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages = messages
    )

    # 多轮对话
    messages.append(response.choices[0].message)
    print(f"\n {messages[-1].content} \n")

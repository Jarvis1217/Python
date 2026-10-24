import random


def generate_secret():
    """生成四位不重复的数字密码"""
    return ''.join(random.sample('0123456789', 4))


def parse_guess(text):
    """校验输入，返回合法的话返回字符串，否则返回 None"""
    if len(text) != 4:
        print("请输入 4 位数字！")
        return None
    if not text.isdigit():
        print("只能输入数字！")
        return None
    if len(set(text)) != 4:
        print("4 位数字不能重复！")
        return None
    return text


def judge(secret, guess):
    """返回 (A, B)：A 数字对且位置对，B 数字对但位置不对"""
    a = sum(s == g for s, g in zip(secret, guess))
    b = len(set(secret) & set(guess)) - a
    return a, b


def main():
    secret = generate_secret()
    tries = 0

    print("=" * 36)
    print("   密码是四位不重复的数字")
    print("   A：数字与位置都对  B：数字对位置错")
    print("=" * 36)

    while True:
        raw = input("请输入你猜的 4 位数字：").strip()

        if raw == "ans":
            print(f"answer = {secret}")
            break

        guess = parse_guess(raw)
        if guess is None:
            continue

        tries += 1
        a, b = judge(secret, guess)
        print(f"{a}A{b}B")

        if a == 4:
            print(f"bingo~，共尝试了{tries}次")
            break


if __name__ == "__main__":
    main()
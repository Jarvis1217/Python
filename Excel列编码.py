def encode(num):
    ans = []
    while num > 0:
        num -= 1
        ans.append(chr(num % 26 + ord("A")))
        num //= 26
    return "".join(ans[::-1])


def decode(word):
    word, ans = word[::-1], 0
    for i in range(len(word)):
        tmp = ord(word[i]) - ord("A")
        ans += (tmp + 1) * (26 ** i)
    return ans


if __name__ == '__main__':
    pass

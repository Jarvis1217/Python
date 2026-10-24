import random
from fractions import Fraction


def solve24(nums):
    """返回所有能算出 24 的表达式（字符串集合）"""
    results = set()

    def helper(items):
        if len(items) == 1:
            if items[0][0] == 24:
                results.add(items[0][1])
            return
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, ea = items[i]
                b, eb = items[j]
                rest = [items[k] for k in range(len(items)) if k != i and k != j]
                cands = [
                    (a + b, f"({ea}+{eb})"),
                    (a * b, f"({ea}*{eb})"),
                    (a - b, f"({ea}-{eb})"),
                    (b - a, f"({eb}-{ea})"),
                ]
                if b != 0:
                    cands.append((a / b, f"({ea}/{eb})"))
                if a != 0:
                    cands.append((b / a, f"({eb}/{ea})"))
                for val, expr in cands:
                    helper(rest + [(val, expr)])

    helper([(Fraction(x), str(x)) for x in nums])
    return results


def main():
    # 反复随机，直到生成的四个数一定有解
    while True:
        nums = [random.randint(1, 9) for _ in range(4)]
        sols = solve24(nums)
        if sols:
            break

    print(f"随机生成的四个数字：{nums}")
    input("按回车键查看答案...")

    # 去掉最外层括号，去重后排序
    shown = sorted({s[1:-1] for s in sols})
    print(f"共找到 {len(shown)} 个不同答案：")
    for idx, s in enumerate(shown, 1):
        print(f"{idx}. {s} = 24")


if __name__ == "__main__":
    main()

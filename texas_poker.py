import random
from itertools import combinations
from collections import Counter

# =========================================================
# 基础牌面定义
# =========================================================
SUITS = ['♠', '♥', '♣', '♦']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

RANK_TO_VALUE = {rank: i + 2 for i, rank in enumerate(RANKS)}
VALUE_TO_RANK = {v: k for k, v in RANK_TO_VALUE.items()}

# 牌型名称，索引与 evaluate_5 的返回等级一一对应
CATEGORY_MAP = [
    "高牌", "一对", "两对", "三条", "顺子",
    "同花", "葫芦", "四条", "同花顺", "皇家同花顺"
]


# =========================================================
# 生成一副标准扑克牌
# =========================================================
def create_deck():
    """
    生成一副 52 张标准扑克牌。
    统一格式为“花色 + 点数”，例如：
    ♠A、♥10、♦K
    """
    return [suit + rank for suit in SUITS for rank in RANKS]


# =========================================================
# 牌面校验
# =========================================================
def validate_cards(cards):
    """
    校验输入牌面是否合法，防止：
    1. 传入重复牌
    2. 传入非法格式
    """
    if len(cards) != len(set(cards)):
        raise ValueError("牌组中存在重复牌")

    for card in cards:
        if not isinstance(card, str) or len(card) < 2:
            raise ValueError(f"非法牌面: {card}")

        suit = card[0]
        rank = card[1:]

        if suit not in SUITS or rank not in RANK_TO_VALUE:
            raise ValueError(f"非法牌面: {card}")


# =========================================================
# 单张牌解析与格式化
# =========================================================
def parse(card):
    """
    将一张牌拆成：(点数数值, 花色)
    """
    return RANK_TO_VALUE[card[1:]], card[0]


def format_card(card):
    """
    输出统一格式“花色 + 点数”
    """
    return f"{card[0]}{card[1:]}"


# =========================================================
# 顺子展示顺序处理
# =========================================================
def straight_values(high):
    """
    根据顺子最高点数，生成顺子展示顺序。
    A2345 需要特殊处理。
    """
    if high == 5:
        return [5, 4, 3, 2, 14]
    return list(range(high, high - 5, -1))


# =========================================================
# 按给定点数顺序重排 5 张牌
# =========================================================
def order_cards(cards5, rank_order):
    """
    按给定的点数顺序，把 5 张牌重新排序。
    例如：
    rank_order = [10, 10, 7, 4, 2]
    就会把两张 10 放到前面，再依次放入 7、4、2。
    """
    remaining = list(cards5)
    ordered = []

    for value in rank_order:
        for i, card in enumerate(remaining):
            if RANK_TO_VALUE[card[1:]] == value:
                ordered.append(card)
                remaining.pop(i)
                break

    return ordered


# =========================================================
# 5 张牌的牌型判断
# =========================================================
def evaluate_5(cards5):
    """
    评估 5 张牌的牌型，并返回一个可比较的元组：
        (牌型等级, 关键比较信息)

    关键比较信息中，数值越大越强，适用于直接做字典序比较。
    """
    ranks = [RANK_TO_VALUE[c[1:]] for c in cards5]
    suits = [c[0] for c in cards5]
    cnt = Counter(ranks)

    # 是否同花
    is_flush = len(set(suits)) == 1

    # 去重后按点数从大到小排序，用来判断顺子
    unique = sorted(set(ranks), reverse=True)

    # 判断顺子：普通顺子或 A2345（轮子顺）
    straight_high = None
    if set([14, 5, 4, 3, 2]).issubset(ranks):
        straight_high = 5
    elif len(unique) == 5 and unique[0] - unique[-1] == 4:
        straight_high = unique[0]

    # 同花顺 / 皇家同花顺
    if is_flush and straight_high:
        if straight_high == 14:
            return (9, [14])
        return (8, [straight_high])

    # 四条
    if 4 in cnt.values():
        four = next(k for k, v in cnt.items() if v == 4)
        kicker = next(k for k in ranks if k != four)
        return (7, [four, kicker])

    # 葫芦
    if sorted(cnt.values()) == [2, 3]:
        three = next(k for k, v in cnt.items() if v == 3)
        pair = next(k for k, v in cnt.items() if v == 2)
        return (6, [three, pair])

    # 同花
    if is_flush:
        return (5, sorted(ranks, reverse=True))

    # 顺子
    if straight_high:
        return (4, [straight_high])

    # 三条
    if 3 in cnt.values():
        three = next(k for k, v in cnt.items() if v == 3)
        kickers = sorted((k for k in ranks if k != three), reverse=True)
        return (3, [three] + kickers)

    # 两对
    pairs = sorted((k for k, v in cnt.items() if v == 2), reverse=True)
    if len(pairs) >= 2:
        kicker = next(k for k in ranks if k not in pairs)
        return (2, pairs[:2] + [kicker])

    # 一对
    if len(pairs) == 1:
        pair = pairs[0]
        kickers = sorted((k for k in ranks if k != pair), reverse=True)
        return (1, [pair] + kickers)

    # 高牌
    return (0, sorted(ranks, reverse=True))


# =========================================================
# 计算 7 张牌中的最佳 5 张牌
# =========================================================
def get_best_hand_value_and_cards(hole_cards, community_cards):
    """
    输入 2 张手牌 + 5 张公共牌，
    返回：
        1. 最佳牌型比较元组 best_val
        2. 最佳 5 张牌 best_cards
    """
    if len(hole_cards) != 2 or len(community_cards) != 5:
        raise ValueError("德州扑克应传入 2 张手牌和 5 张公共牌")

    cards = hole_cards + community_cards
    validate_cards(cards)

    best_val = None
    best_cards = None

    for comb in combinations(cards, 5):
        val = evaluate_5(comb)
        if best_val is None or val > best_val:
            best_val = val
            best_cards = list(comb)

    return best_val, best_cards


# =========================================================
# 生成展示顺序
# =========================================================
def build_display_order(cards5, category, tiebreak):
    """
    根据牌型生成更适合展示的顺序。

    说明：
    - 顺子 / 同花 / 高牌：按点数从大到小
    - 一对 / 两对 / 三条 / 葫芦 / 四条：需要把重复点数也写入顺序，
      这样才能完整输出 5 张牌，而不是只显示“一张对子牌”
    """
    ranks = [RANK_TO_VALUE[c[1:]] for c in cards5]
    cnt = Counter(ranks)

    if category in (9, 8, 4):
        # 皇家同花顺 / 同花顺 / 顺子
        return straight_values(tiebreak[0])

    if category == 7:
        # 四条：四张相同点数 + 1 张踢脚牌
        four = next(k for k, v in cnt.items() if v == 4)
        kicker = next(k for k in sorted(ranks, reverse=True) if k != four)
        return [four] * 4 + [kicker]

    if category == 6:
        # 葫芦：三条 + 一对
        three = next(k for k, v in cnt.items() if v == 3)
        pair = next(k for k, v in cnt.items() if v == 2)
        return [three] * 3 + [pair] * 2

    if category == 3:
        # 三条：三张相同点数 + 2 张踢脚牌
        three = next(k for k, v in cnt.items() if v == 3)
        kickers = sorted((k for k in ranks if k != three), reverse=True)
        return [three] * 3 + kickers

    if category == 2:
        # 两对：高对 + 低对 + 1 张踢脚牌
        pairs = sorted((k for k, v in cnt.items() if v == 2), reverse=True)
        kicker = next(k for k in sorted(ranks, reverse=True) if k not in pairs)
        return [pairs[0]] * 2 + [pairs[1]] * 2 + [kicker]

    if category == 1:
        # 一对：对子 + 3 张踢脚牌
        pair = next(k for k, v in cnt.items() if v == 2)
        kickers = sorted((k for k in ranks if k != pair), reverse=True)
        return [pair] * 2 + kickers

    # 同花 / 高牌：直接按点数从大到小
    return sorted(ranks, reverse=True)


# =========================================================
# 返回最佳牌型描述
# =========================================================
def best_poker_hand_with_cards(hole_cards, community_cards):
    """
    返回类似：
    “皇家同花顺：♠A，♠K，♠Q，♠J，♠10”

    说明：
    - 一对、两对也会完整输出 5 张牌
    - 展示顺序按牌型习惯排列
    """
    best_val, best_cards = get_best_hand_value_and_cards(hole_cards, community_cards)

    category = best_val[0]
    tiebreak = best_val[1]

    rank_order = build_display_order(best_cards, category, tiebreak)
    ordered_cards = order_cards(best_cards, rank_order)
    result_cards = "，".join(format_card(c) for c in ordered_cards)

    return f"{CATEGORY_MAP[category]}：{result_cards}"


# =========================================================
# 比较玩家和电脑的胜负
# =========================================================
def compare_winner(player_cards, computer_cards, community_cards):
    """
    比较玩家与电脑的最佳牌型，返回：
        “玩家获胜”
        “电脑获胜”
        “和局”
    """
    player_val, _ = get_best_hand_value_and_cards(player_cards, community_cards)
    computer_val, _ = get_best_hand_value_and_cards(computer_cards, community_cards)

    if player_val > computer_val:
        return "玩家获胜"
    if computer_val > player_val:
        return "电脑获胜"
    return "和局"


# =========================================================
# 主程序：发牌并展示结果
# =========================================================
def main():
    deck = create_deck()
    random.shuffle(deck)

    # 发手牌
    player = [deck.pop() for _ in range(2)]
    computer = [deck.pop() for _ in range(2)]

    # 发公共牌
    community = [deck.pop() for _ in range(5)]

    print("玩家手牌:", " ".join(format_card(c) for c in player))
    print("电脑手牌:", " ".join(format_card(c) for c in computer), "\n")

    print("公共牌:", " ".join(format_card(c) for c in community), "\n")

    print(f"玩家：{best_poker_hand_with_cards(player, community)}")
    print(f"电脑：{best_poker_hand_with_cards(computer, community)}", "\n")
    
    # 输出最终胜负结果
    print(compare_winner(player, computer, community))


if __name__ == "__main__":
    main()

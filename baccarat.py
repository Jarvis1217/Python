import random


def create_deck():
    """生成一副不含大小王的52张扑克牌"""
    suits = ['♠', '♥', '♣', '♦']
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    deck = []

    for suit in suits:
        for rank in ranks:
            deck.append(f"{suit}{rank}")

    return deck


def card_value(card):
    """返回单张牌在百家乐中的点数值"""
    rank = card[1:] if card[1] != '1' else card[1:]  # 兼容10
    if rank in ["J", "Q", "K", "10"]:
        return 0
    elif rank == "A":
        return 1
    else:
        return int(rank)


def hand_point(hand):
    """计算一手牌的点数总和（只取个位数）"""
    total = sum(card_value(card) for card in hand)
    return total % 10


def banker_should_draw(banker_point, player_third_value):
    """
    庄家补牌规则：
    1. 庄家点数 0~2：必补
    2. 庄家点数 3：当闲家第三张不是8时补牌
    3. 庄家点数 4：闲家第三张为2~7时补牌
    4. 庄家点数 5：闲家第三张为4~7时补牌
    5. 庄家点数 6：闲家第三张为6~7时补牌
    6. 庄家点数 7：停牌
    """
    if banker_point <= 2:
        return True
    if banker_point == 3:
        return player_third_value != 8
    if banker_point == 4:
        return player_third_value is not None and 2 <= player_third_value <= 7
    if banker_point == 5:
        return player_third_value is not None and 4 <= player_third_value <= 7
    if banker_point == 6:
        return player_third_value is not None and 6 <= player_third_value <= 7
    return False


def baccarat_round():
    """模拟一局百家乐"""
    # 1. 生成并洗牌
    deck = create_deck()
    random.shuffle(deck)

    # 2. 发初始牌：闲、庄各两张
    player_hand = [deck.pop(), deck.pop()]
    banker_hand = [deck.pop(), deck.pop()]

    # 3. 输出初始牌
    print("闲家手牌：", player_hand)
    print("庄家手牌：", banker_hand)

    player_point = hand_point(player_hand)
    banker_point = hand_point(banker_hand)

    # 4. 判断是否天牌（8点或9点）
    if player_point in [8, 9] or banker_point in [8, 9]:
        print("闲家无需补牌")
        print("庄家无需补牌")
    else:
        # 5. 闲家补牌规则：0~5补牌，6~7停牌
        if player_point <= 5:
            player_hand.append(deck.pop())
            print("闲家补牌结果：", player_hand)
            player_third_value = card_value(player_hand[2])
        else:
            print("闲家无需补牌")
            player_third_value = None

        # 6. 庄家补牌规则
        banker_point = hand_point(banker_hand)
        if banker_should_draw(banker_point, player_third_value):
            banker_hand.append(deck.pop())
            print("庄家补牌结果：", banker_hand)
        else:
            print("庄家无需补牌")

    # 7. 计算最终点数并判断输赢
    player_point = hand_point(player_hand)
    banker_point = hand_point(banker_hand)

    print(f"闲家最终点数：{player_point}")
    print(f"庄家最终点数：{banker_point}")

    if player_point > banker_point:
        print("闲赢")
    elif player_point < banker_point:
        print("庄赢")
    else:
        print("和局")


if __name__ == "__main__":
    baccarat_round()

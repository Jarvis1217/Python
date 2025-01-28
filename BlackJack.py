import random

# 定义牌组
SUITS = ['♠', '♣', '♦', '♥']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}

# 创建牌组
def create_deck():
    deck = [(rank, suit) for rank in RANKS for suit in SUITS]
    random.shuffle(deck)
    return deck

# 计算手牌的点数
def calculate_hand_value(hand):
    value = sum(VALUES[card[0]] for card in hand)
    # 处理A作为1点或11点的情况
    aces = sum(1 for card in hand if card[0] == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

# 显示手牌
def display_hand(hand):
    return ' '.join([f'{card[0]}{card[1]}' for card in hand])

# 玩家行动
def player_turn(deck, player_hand):
    while True:
        print(f"你的手牌：{display_hand(player_hand)} 当前点数：{calculate_hand_value(player_hand)}")
        if calculate_hand_value(player_hand) > 21:
            print("爆牌！你输了！")
            return False
        action = input("要牌 (h) 或停牌 (s)：").lower()
        if action == 'h':  # 玩家选择要牌
            player_hand.append(deck.pop())
        elif action == 's':  # 玩家选择停牌
            return True

# 庄家行动
def dealer_turn(deck, dealer_hand):
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.pop())
    return dealer_hand

# 游戏主流程
def blackjack_game():
    # 初始化游戏
    deck = create_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    # 显示庄家明牌
    print(f"庄家的明牌：{dealer_hand[0][0]}{dealer_hand[0][1]}")

    # 玩家回合
    if not player_turn(deck, player_hand):
        return  # 玩家爆牌，游戏结束

    # 庄家回合
    dealer_hand = dealer_turn(deck, dealer_hand)
    print(f"庄家的手牌：{display_hand(dealer_hand)} 当前点数：{calculate_hand_value(dealer_hand)}")

    # 比较点数
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)
    if dealer_value > 21:
        print("庄家爆牌，你赢了！")
    elif player_value > dealer_value:
        print("你赢了！")
    elif player_value < dealer_value:
        print("庄家赢了！")
    else:
        print("平局！")

# 开始游戏
if __name__ == "__main__":
    blackjack_game()

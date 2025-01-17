import random
import time

# 生成乱序牌组
def generate_shuffled_deck():
    suits = ['♤', '♡', '♧', '♢']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    deck = [rank + suit for suit in suits for rank in ranks]

    random.shuffle(deck)

    return deck

# 发牌
def deal_cards(deck, num):
    if num > len(deck):
        raise ValueError("没有足够的牌!")
    
    dealt_cards = deck[-num:]
    del deck[-num:]
    return dealt_cards

deck = generate_shuffled_deck()

computer = deal_cards(deck,2)
player = deal_cards(deck,2)
community  = deal_cards(deck,5)

print(f"公共牌是: {','.join(community)}")

input()
print(f"您的手牌是: {','.join(player)}")

input()
print(f"电脑手牌是: {','.join(computer)}")

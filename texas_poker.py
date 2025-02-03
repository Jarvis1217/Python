import random

suits = ['♠', '♥', '♣', '♦']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

deck = [rank + suit for suit in suits for rank in ranks]

random.shuffle(deck)

player = [deck.pop() for _ in range(2)]
computer = [deck.pop() for _ in range(2)]
community = [deck.pop() for _ in range(5)]

print('电脑手牌: ' + ' '.join(computer))
print('玩家手牌: ' + ' '.join(player))

input()
print('翻牌: ' + ' '.join(community[:3]))

input()
print('转牌: ' + ' '.join(community[:4]))

input()
print('河牌: ' + ' '.join(community[:5]))

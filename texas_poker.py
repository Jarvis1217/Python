import tkinter as tk
import random

# 初始化扑克牌
suits = ['♠', '♥', '♣', '♦']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

deck = [(rank, suit) for suit in suits for rank in ranks]

random.shuffle(deck)

# 初始化Tk窗口
root = tk.Tk()
root.title("Texas poker")
root.configure(bg="green")
root.resizable(False, False)

rows = 3
cols = 5

# 发手牌
for row in [0, 2]:
    for col in range(2):
        card_label = tk.Label(root, width=8, height=6, relief="solid", anchor="nw")
        card_label.grid(row=row, column=col, padx=10, pady=20)

        rank, suit = deck.pop()

        card_label.config(
            text=f"{rank}",
            font=("Arial", 10),
            justify="left"
        )

        suit_color = "red" if suit in ["♥", "♦"] else "black"
        suit_label = tk.Label(card_label, text=suit, font=("Arial", 24), fg=suit_color)
        suit_label.place(relx=0.5, rely=0.5, anchor="center")

# 处理公共牌
community_cards = []
current_step = 0

for col in range(cols):
    card_label = tk.Label(root, width=8, height=6, relief="solid", anchor="nw")
    card_label.grid(row=1, column=col, padx=10, pady=10)
    community_cards.append(card_label)
    card_label.grid_remove()  # 初始隐藏

    rank, suit = deck.pop()

    card_label.config(
        text=f"{rank}",
        font=("Arial", 10),
        justify="left"
    )

    suit_color = "red" if suit in ["♥", "♦"] else "black"
    suit_label = tk.Label(card_label, text=suit, font=("Arial", 24), fg=suit_color)      
    suit_label.place(relx=0.5, rely=0.5, anchor="center")

# 绑定回车事件
def handle_key(event):
    global current_step
    if current_step == 0:
        for i in range(3):
            community_cards[i].grid()
        current_step += 1
    elif current_step == 1:
        community_cards[3].grid()
        current_step += 1
    elif current_step == 2:
        community_cards[4].grid()
        current_step += 1

root.bind('<Return>', handle_key)

root.mainloop()

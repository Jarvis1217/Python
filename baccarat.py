import random
import os
from typing import List, Optional, Tuple

# -----------------------------
# 数据结构定义
# -----------------------------
# 一张牌用三元组表示：(牌面rank, 花色suit, 百家乐点数point)
# 例如：("A", "♠", 1)、("K", "♥", 0)
Card = Tuple[str, str, int]


# -----------------------------
# 牌与点数相关函数
# -----------------------------
def baccarat_point(rank: str) -> int:
    """
    根据牌面返回百家乐点数：
    A = 1
    2~9 = 牌面数字
    10/J/Q/K = 0
    """
    if rank == "A":
        return 1
    if rank in {"J", "Q", "K", "10"}:
        return 0
    # 其余为数字牌：2~9
    return int(rank)


def create_shoe(num_decks: int = 8) -> List[Card]:
    """
    创建一副“牌靴”（多副牌混合），并洗牌。
    百家乐赌场常用 6~8 副牌，这里默认 8 副。
    """
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    suits = ["♠", "♥", "♦", "♣"]

    shoe: List[Card] = []
    for _ in range(num_decks):
        for suit in suits:
            for rank in ranks:
                shoe.append((rank, suit, baccarat_point(rank)))

    random.shuffle(shoe)
    return shoe


def draw_card(shoe: List[Card]) -> Card:
    """
    从牌靴顶端抽一张牌。
    """
    return shoe.pop()


def hand_total(cards: List[Card]) -> int:
    """
    计算手牌点数（取个位数）：
    例如：7 + 8 = 15 -> 5
    """
    return sum(card[2] for card in cards) % 10


def format_cards(cards: List[Card]) -> str:
    """
    将一手牌格式化为可读字符串。
    """
    return " ".join([f"{rank}{suit}" for (rank, suit, _) in cards])


# -----------------------------
# 补牌规则（标准百家乐）
# -----------------------------
def player_should_draw(player_total: int) -> bool:
    """
    闲家（Player/闲）补牌规则：
    - 点数 0~5：补一张
    - 点数 6~7：不补
    （自然牌 8~9 已在主流程先判断，不会走到这里）
    """
    return player_total <= 5


def banker_should_draw(
    banker_total: int,
    player_third_point: Optional[int],
) -> bool:
    """
    庄家（Banker/庄）补牌规则（标准表）：

    1) 如果闲家没有第三张（player_third_point 为 None）：
       - 庄点数 0~5：补牌
       - 庄点数 6~7：不补

    2) 如果闲家补了第三张（player_third_point 为 0~9）：
       - 庄 0~2：总是补
       - 庄 3：除非闲第三张为 8，否则补
       - 庄 4：闲第三张为 2~7 才补
       - 庄 5：闲第三张为 4~7 才补
       - 庄 6：闲第三张为 6~7 才补
       - 庄 7：不补

    注：自然牌 8~9 已在主流程先判断，不会走到这里。
    """
    # 情况1：闲家未补第三张
    if player_third_point is None:
        return banker_total <= 5

    # 情况2：闲家补了第三张，根据闲第三张点数决定
    pt = player_third_point

    if banker_total <= 2:
        return True
    if banker_total == 3:
        return pt != 8
    if banker_total == 4:
        return 2 <= pt <= 7
    if banker_total == 5:
        return 4 <= pt <= 7
    if banker_total == 6:
        return pt in (6, 7)
    # banker_total == 7
    return False


# -----------------------------
# 结果判定与交互
# -----------------------------
def decide_outcome(player_cards: List[Card], banker_cards: List[Card]) -> str:
    """
    根据最终点数判断胜负：
    返回值为："闲赢" / "庄赢" / "和牌"
    """
    pt = hand_total(player_cards)
    bt = hand_total(banker_cards)

    if pt > bt:
        return "闲赢"
    if bt > pt:
        return "庄赢"
    return "和牌"


def read_bet_choice() -> str:
    """
    读取玩家下注选择，并规范化为：
    - "庄赢"
    - "闲赢"
    - "和牌"
    """
    mapping = {
        "1": "庄赢",
        "2": "闲赢",
        "3": "和牌",
    }

    while True:
        print("请选择下注：")
        print("  1) 庄赢")
        print("  2) 闲赢")
        print("  3) 和牌")
        s = input("请输入 1/2/3：").strip().lower()

        if s in mapping:
            return mapping[s]

        print("输入无效，请重新输入。\n")


def main():
    # 创建牌靴（8副牌混洗）
    shoe = create_shoe(num_decks=8)

    print("========== 控制台百家乐 ==========")
    print("规则说明：本程序按标准百家乐补牌规则进行演示与游玩。\n")

    while True:
        # 如果牌靴剩余牌数过少，重新洗牌（保证一局至少能顺利发到第六张）
        # 说明：一局最多会发 6 张（闲2+可能补1，庄2+可能补1）
        if len(shoe) < 20:
            shoe = create_shoe(num_decks=8)
            print("（牌靴牌数不足，已自动重新洗牌）\n")

        bet = read_bet_choice()
        print(f"\n你选择下注：{bet}\n")

        # 按常见发牌顺序：闲、庄、闲、庄
        player_cards: List[Card] = [draw_card(shoe)]
        banker_cards: List[Card] = [draw_card(shoe)]
        player_cards.append(draw_card(shoe))
        banker_cards.append(draw_card(shoe))

        # 展示双方两张手牌
        player_total_2 = hand_total(player_cards)
        banker_total_2 = hand_total(banker_cards)

        print("----- 发牌结果（各两张）-----")
        print(f"闲家手牌：{format_cards(player_cards)}  | 点数：{player_total_2}")
        print(f"庄家手牌：{format_cards(banker_cards)}  | 点数：{banker_total_2}")
        print()

        # 先判断是否为自然牌（天牌）：任意一方两张合计 8 或 9
        # 自然牌出现则双方都不再补牌，直接比点数定胜负
        if player_total_2 in (8, 9) or banker_total_2 in (8, 9):
            print("出现自然牌（天牌）：双方不补牌，直接结算。\n")
        else:
            # -----------------------------
            # 1) 判断闲家是否需要补牌
            # -----------------------------
            player_third: Optional[Card] = None
            if player_should_draw(player_total_2):
                player_third = draw_card(shoe)
                player_cards.append(player_third)
                print("闲家点数 0~5，需要补牌。")
                print(f"闲家补牌：{player_third[0]}{player_third[1]}（点数 {player_third[2]}）")
            else:
                print("闲家点数 6~7，不补牌。")

            # 补牌后展示闲家当前状态
            print(f"闲家当前手牌：{format_cards(player_cards)}  | 点数：{hand_total(player_cards)}")
            print()

            # -----------------------------
            # 2) 判断庄家是否需要补牌
            # -----------------------------
            banker_total_now = hand_total(banker_cards)
            player_third_point = player_third[2] if player_third is not None else None

            if banker_should_draw(banker_total_now, player_third_point):
                banker_third = draw_card(shoe)
                banker_cards.append(banker_third)
                print("庄家需要补牌。")
                print(f"庄家补牌：{banker_third[0]}{banker_third[1]}（点数 {banker_third[2]}）")
            else:
                print("庄家不补牌。")

            print(f"庄家最终手牌：{format_cards(banker_cards)}  | 点数：{hand_total(banker_cards)}")
            print()

        # -----------------------------
        # 3) 补牌结束，判定胜负
        # -----------------------------
        final_player_total = hand_total(player_cards)
        final_banker_total = hand_total(banker_cards)
        outcome = decide_outcome(player_cards, banker_cards)

        print("========== 本局结算 ==========")
        print(f"闲家最终：{format_cards(player_cards)}  | 点数：{final_player_total}")
        print(f"庄家最终：{format_cards(banker_cards)}  | 点数：{final_banker_total}")
        print(f"结果：{outcome}")
        print()

        # -----------------------------
        # 4) 对比玩家下注与结果
        # -----------------------------
        if bet == outcome:
            print("你的下注命中：你赢了！")
        else:
            # 常见赌场规则：如果你押庄/闲，但开出和牌，通常是“退回本金（push）”
            # 这里没有金额系统，给出提示即可
            if outcome == "和牌" and bet in ("庄赢", "闲赢"):
                print("本局为和牌：按常见规则庄/闲下注通常退回（本程序提示为：不输不赢）。")
            else:
                print("你的下注未命中：你输了。")

        print()

        # 是否继续
        again = input("是否再来一局？(y/n)：").strip().lower()
        print()
        if again not in ("y", "yes", "是", "继续"):
            print("游戏结束！")
            break

        os.system("cls")


if __name__ == "__main__":
    main()
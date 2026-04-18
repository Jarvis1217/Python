import pygame
import sys
import random
import texas

# ==================== 初始化 Pygame ====================
pygame.init()
WINDOW_WIDTH = 800   # 默认宽度
WINDOW_HEIGHT = 600  # 默认高度
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("德州扑克")

# 颜色常量
BG_COLOR = (0, 81, 44)
BUTTON_COLOR = (70, 130, 100)
BUTTON_HOVER = (100, 160, 130)
TEXT_COLOR = (255, 255, 255)
INFO_BG = (20, 60, 40)

# 字体辅助函数：优先使用华文仿宋
def get_font(size, bold=False):
    """尝试加载华文仿宋，失败则回退到其他中文字体"""
    fonts = ["华文仿宋", "SimHei", "Microsoft YaHei", "Arial"]
    for f in fonts:
        try:
            return pygame.font.SysFont(f, size, bold=bold)
        except:
            continue
    return pygame.font.Font(None, size)  # 最终回退

# 时钟
clock = pygame.time.Clock()

# ==================== 牌图片处理 ====================
# 原始图片尺寸
ORIG_CARD_W = 420
ORIG_CARD_H = 600

# 花色映射 (texas 符号 -> 图片文件夹中的中文名)
SUIT_MAP = {
    '♠': '黑桃',
    '♥': '红心',
    '♣': '梅花',
    '♦': '方片'
}

def load_card_images():
    """加载 poker 文件夹中的所有牌图片，返回原始尺寸的 Surface 字典"""
    card_images = {}
    for suit_symbol, suit_name in SUIT_MAP.items():
        for rank in texas.RANKS:
            filename = f"poker/{suit_name}{rank}.png"
            try:
                img = pygame.image.load(filename).convert_alpha()
                card_images[(suit_symbol, rank)] = img
            except FileNotFoundError:
                print(f"警告: 找不到图片 {filename}")
                # 创建一张占位牌
                surf = pygame.Surface((ORIG_CARD_W, ORIG_CARD_H))
                surf.fill((200, 200, 200))
                pygame.draw.rect(surf, (0,0,0), surf.get_rect(), 2)
                font = pygame.font.Font(None, 80)
                text = font.render(f"{suit_name}{rank}", True, (0,0,0))
                surf.blit(text, (50, 250))
                card_images[(suit_symbol, rank)] = surf
    return card_images

# 加载原始图片
ORIG_CARD_IMAGES = load_card_images()

def create_card_back_orig():
    """生成原始尺寸的背面图案"""
    back = pygame.Surface((ORIG_CARD_W, ORIG_CARD_H))
    back.fill((30, 30, 80))
    for i in range(0, ORIG_CARD_W, 40):
        pygame.draw.line(back, (100, 100, 180), (i, 0), (i, ORIG_CARD_H))
    for j in range(0, ORIG_CARD_H, 40):
        pygame.draw.line(back, (100, 100, 180), (0, j), (ORIG_CARD_W, j))
    pygame.draw.rect(back, (200, 200, 255), back.get_rect(), 10)
    return back

ORIG_CARD_BACK = create_card_back_orig()

# 缩放缓存：避免每帧重复缩放
scaled_cache = {}

def get_scaled_card_image(card_str, target_width, target_height):
    """根据目标尺寸返回缩放后的牌面图片（带缓存）"""
    key = (card_str, target_width, target_height)
    if key in scaled_cache:
        return scaled_cache[key]
    orig = ORIG_CARD_IMAGES.get((card_str[0], card_str[1:]), ORIG_CARD_BACK)
    scaled = pygame.transform.smoothscale(orig, (target_width, target_height))
    scaled_cache[key] = scaled
    return scaled

def get_scaled_back_image(target_width, target_height):
    key = ("back", target_width, target_height)
    if key in scaled_cache:
        return scaled_cache[key]
    scaled = pygame.transform.smoothscale(ORIG_CARD_BACK, (target_width, target_height))
    scaled_cache[key] = scaled
    return scaled

# ==================== 游戏状态管理 ====================
class PokerGame:
    def __init__(self):
        self.deck = []
        self.player_hand = []      # 2张
        self.computer_hand = []    # 2张
        self.community = []        # 0~5张
        self.stage = 0             # 0:未发公共牌, 1:flop, 2:turn, 3:river
        self.winner_text = ""
        self.player_hand_desc = ""
        self.computer_hand_desc = ""
        self.new_game()

    def new_game(self):
        """重新开始一局"""
        self.deck = texas.create_deck()
        random.shuffle(self.deck)
        self.player_hand = [self.deck.pop() for _ in range(2)]
        self.computer_hand = [self.deck.pop() for _ in range(2)]
        self.community = []
        self.stage = 0
        self.winner_text = ""
        self.player_hand_desc = ""
        self.computer_hand_desc = ""
        self.update_descriptions()

    def deal_community(self):
        """根据当前阶段发公共牌"""
        if self.stage == 0 and len(self.deck) >= 3:
            self.community.extend([self.deck.pop() for _ in range(3)])
            self.stage = 1
        elif self.stage == 1 and len(self.deck) >= 1:
            self.community.append(self.deck.pop())
            self.stage = 2
        elif self.stage == 2 and len(self.deck) >= 1:
            self.community.append(self.deck.pop())
            self.stage = 3
            self.evaluate_winner()
        self.update_descriptions()

    def update_descriptions(self):
        if len(self.community) == 5:
            try:
                self.player_hand_desc = texas.best_poker_hand_with_cards(self.player_hand, self.community)
                self.computer_hand_desc = texas.best_poker_hand_with_cards(self.computer_hand, self.community)
            except:
                self.player_hand_desc = "计算错误"
                self.computer_hand_desc = "计算错误"
        else:
            self.player_hand_desc = f"等待公共牌"
            self.computer_hand_desc = f"等待公共牌"

    def evaluate_winner(self):
        if len(self.community) != 5:
            return
        try:
            result = texas.compare_winner(self.player_hand, self.computer_hand, self.community)
            self.winner_text = f"{result}"
        except:
            self.winner_text = "比较出错"

# ==================== 自适应布局绘制 ====================
def draw_game(game):
    """根据当前屏幕尺寸绘制整个界面"""
    screen = pygame.display.get_surface()
    w, h = screen.get_size()
    
    # 基础比例因子（基于 800x600 设计）
    scale_x = w / 800
    scale_y = h / 600
    scale = min(scale_x, scale_y)  # 统一缩放，保持比例
    
    # 计算卡片大小（原始宽高比 420:600 = 0.7）
    card_w = int(105 * scale)
    card_h = int(150 * scale)
    # 卡片间距
    card_gap = int(15 * scale)
    
    # 按钮尺寸
    btn_w = int(140 * scale_x)
    btn_h = int(40 * scale_y)
    
    # 字体大小
    title_size = int(36 * scale)
    label_size = int(28 * scale)
    small_size = int(20 * scale)
    info_size = int(22 * scale)
    
    font_title = get_font(title_size, bold=True)
    font_label = get_font(label_size)
    font_small = get_font(small_size)
    font_info = get_font(info_size)
    
    # 清屏
    screen.fill(BG_COLOR)
    
    # 电脑手牌绘制（居中）
    comp_cards_count = len(game.computer_hand)
    comp_total_width = comp_cards_count * card_w + (comp_cards_count - 1) * card_gap
    comp_start_x = w//2 - comp_total_width//2
    comp_y = int(50 * scale_y)
    for i, card in enumerate(game.computer_hand):
        img = get_scaled_card_image(card, card_w, card_h)
        x = comp_start_x + i * (card_w + card_gap)
        screen.blit(img, (x, comp_y))
    
    # ---------- 公共牌区域 (中部) ----------
    comm_total_width = 5 * card_w + 4 * card_gap
    comm_start_x = w//2 - comm_total_width//2
    comm_y = int(240 * scale_y)
    for i in range(5):
        x = comm_start_x + i * (card_w + card_gap)
        if i < len(game.community):
            img = get_scaled_card_image(game.community[i], card_w, card_h)
        else:
            img = get_scaled_back_image(card_w, card_h)
        screen.blit(img, (x, comm_y))
    
    # 阶段文字
    stage_names = ["未发公共牌", "翻牌 (Flop)", "转牌 (Turn)", "河牌 (River)"]
    stage_text = font_small.render(stage_names[game.stage], True, (220, 220, 150))
    stage_x = comm_start_x
    stage_y = comm_y + card_h + int(5 * scale_y)
    screen.blit(stage_text, (stage_x, stage_y))
    
    # ---------- 玩家区域 (下方) ----------
    player_cards_count = len(game.player_hand)
    player_total_width = player_cards_count * card_w + (player_cards_count - 1) * card_gap
    player_start_x = w//2 - player_total_width//2
    player_y = int(420 * scale_y)
    for i, card in enumerate(game.player_hand):
        img = get_scaled_card_image(card, card_w, card_h)
        x = player_start_x + i * (card_w + card_gap)
        screen.blit(img, (x, player_y))
    
    # ---------- 信息面板 (左侧) ----------
    info_x = int(30 * scale_x)
    info_y = int(480 * scale_y)
    line_height = int(35 * scale_y)
    
    # 带背景的文字
    def draw_info_text(text, y, font, color=TEXT_COLOR):
        txt_surf = font.render(text, True, color)
        txt_rect = txt_surf.get_rect(topleft=(info_x, y))
        bg_rect = txt_rect.inflate(16, 8)
        pygame.draw.rect(screen, INFO_BG, bg_rect, border_radius=6)
        screen.blit(txt_surf, txt_rect)
        return txt_rect.bottom
    
    y_pos = info_y
    y_pos = draw_info_text(f"电脑: {game.computer_hand_desc}", y_pos, font_info) + 10
    y_pos = draw_info_text(f"玩家: {game.player_hand_desc}", y_pos, font_info) + 10
    if game.winner_text:
        draw_info_text(game.winner_text, y_pos, font_label, (255, 255, 180))
    
    # ---------- 按钮区域 (右侧) ----------
    btn_x = w - btn_w - int(30 * scale_x)
    btn_y = int(480 * scale_y)
    btn_gap = int(20 * scale_y)
    
    mouse_pos = pygame.mouse.get_pos()
    
    # 发公共牌按钮
    deal_enabled = game.stage < 3
    deal_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    deal_hover = deal_enabled and deal_rect.collidepoint(mouse_pos)
    color = BUTTON_HOVER if deal_hover else BUTTON_COLOR
    pygame.draw.rect(screen, color, deal_rect, border_radius=8)
    pygame.draw.rect(screen, (200, 230, 200), deal_rect, 2, border_radius=8)
    deal_txt = font_label.render("发公共牌", True, TEXT_COLOR)
    deal_txt_rect = deal_txt.get_rect(center=deal_rect.center)
    screen.blit(deal_txt, deal_txt_rect)
    
    # 重新开始按钮
    restart_rect = pygame.Rect(btn_x, btn_y + btn_h + btn_gap, btn_w, btn_h)
    restart_hover = restart_rect.collidepoint(mouse_pos)
    color = BUTTON_HOVER if restart_hover else BUTTON_COLOR
    pygame.draw.rect(screen, color, restart_rect, border_radius=8)
    pygame.draw.rect(screen, (200, 230, 200), restart_rect, 2, border_radius=8)
    restart_txt = font_label.render("重新发牌", True, TEXT_COLOR)
    restart_txt_rect = restart_txt.get_rect(center=restart_rect.center)
    screen.blit(restart_txt, restart_txt_rect)
    
    return deal_rect, restart_rect

# ==================== 主循环 ====================
def main():
    game = PokerGame()
    deal_rect = restart_rect = quit_rect = pygame.Rect(0,0,0,0)
    running = True
    
    # 初始设置窗口
    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # 调整窗口大小，清空缓存，并更新显示模式
                scaled_cache.clear()
                pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if deal_rect.collidepoint(mouse_pos) and game.stage < 3:
                    game.deal_community()
                elif restart_rect.collidepoint(mouse_pos):
                    game.new_game()
                elif quit_rect.collidepoint(mouse_pos):
                    running = False
        
        # 绘制（内部使用 pygame.display.get_surface() 获取当前屏幕）
        deal_rect, restart_rect = draw_game(game)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
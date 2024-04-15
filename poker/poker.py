import pygame
import random
import os

# 初始化pygame
pygame.init()

# 设置窗口大小，使用pygame.RESIZABLE标志使窗口可以调整大小
screen = pygame.display.set_mode((1000, 600), pygame.RESIZABLE)

# 设置窗口标题
pygame.display.set_caption('poker')

# 扑克牌的花色和数字
suits = ['黑桃', '红心', '方片', '梅花']
numbers = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

# 加载扑克牌图片
cards = []
for suit in suits:
    for number in numbers:
        image = pygame.image.load(os.path.join('img', f'{suit}{number}.jpg'))
        cards.append(image)

# 加载扑克牌背景
background = pygame.image.load(os.path.join('img', 'poker_back.jpg'))

# 发牌动作循环标志
deal_cards_flag = -1

# 设置按钮颜色
button_color = (0, 255, 0)
text_color = (255, 255, 255)

# 创建字体对象
font = pygame.font.Font(".\\JianTi.ttf", 30)

# 绘制按钮
screen_width, screen_height = pygame.display.get_surface().get_size() # 确定左边距和上边距
left, up = screen_width - 250, screen_height - 80

def draw_deal_button():
    pygame.draw.rect(screen, button_color, (left, up, 100, 50))
    text = font.render('发牌', True, text_color)
    screen.blit(text, (left + 20, up + 8))

# 主循环
running = True
while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            # 窗口大小改变，更新窗口大小
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            screen_width, screen_height = pygame.display.get_surface().get_size() # 确定左边距和上边距
            left, up = screen_width - 250, screen_height - 80
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 获取鼠标位置
            x, y = pygame.mouse.get_pos()
            # 检查鼠标是否在按钮上
            if left < x < left + 100 and up < y < up + 50:
                deal_cards_flag = 0

    # 桌面背景颜色
    screen.fill((0, 128, 0))

    # 绘制按钮
    draw_deal_button()

    # 绘制扑克牌背景
    bg_width, bg_height = background.get_size()
    bg_width, bg_height = bg_width + 20, bg_height + 20 # 与窗口边缘间距
    screen_width, screen_height = pygame.display.get_surface().get_size()
    screen.blit(background, (screen_width - bg_width, screen_height - bg_height))

    # 发牌动画
    if deal_cards_flag == 0:
        random.shuffle(cards) # 洗牌
        for i, card in enumerate(cards):
            x = i % 13 * 60 + 10
            y = i // 13 * 90 + 10
            screen.blit(card, (x, y))
            pygame.display.flip()
            pygame.time.wait(50)  # 暂停50毫秒来模拟发牌的动作
            deal_cards_flag += 1

    if deal_cards_flag == 52:
        # 绘制扑克牌
        for i, card in enumerate(cards):
            x = i % 13 * 60 + 10
            y = i // 13 * 90 + 10
            screen.blit(card, (x, y))

    # 更新屏幕
    pygame.display.update()

# 退出pygame
pygame.quit()

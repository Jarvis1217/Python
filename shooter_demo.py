import pygame
import sys
import random

# 初始化
pygame.init()

# 定义颜色
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# 设置窗口大小
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# 创建窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Game_Demo')

# 定义英雄属性
hero_width = 30
hero_height = 50
hero_x = 10
hero_y = (WINDOW_HEIGHT // 2) - (hero_height // 2)
hero_speed = 5

# 定义子弹属性
bullets = []
bullet_radius = 5
bullet_speed = 7

# 定义敌人属性
enemies = []
enemy_width = 30
enemy_height = 50
enemy_speed = 3
spawn_delay = 90  # 每隔 90 帧生成一个敌人
spawn_timer = 0

# 游戏循环
clock = pygame.time.Clock()

def draw_grid():
    grid_size = 50
    for x in range(0, WINDOW_WIDTH, grid_size):
        pygame.draw.line(screen, WHITE, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, grid_size):
        pygame.draw.line(screen, WHITE, (0, y), (WINDOW_WIDTH, y))

def move_hero(keys_pressed):
    global hero_x, hero_y
    if keys_pressed[pygame.K_w] and hero_y - hero_speed > 0:  # 向上
        hero_y -= hero_speed
    if keys_pressed[pygame.K_s] and hero_y + hero_speed + hero_height < WINDOW_HEIGHT:  # 向下
        hero_y += hero_speed
    if keys_pressed[pygame.K_a] and hero_x - hero_speed > 0:  # 向左
        hero_x -= hero_speed
    if keys_pressed[pygame.K_d] and hero_x + hero_speed + hero_width < WINDOW_WIDTH:  # 向右
        hero_x += hero_speed

def handle_bullets():
    global bullets, enemies
    for bullet in bullets[:]:
        bullet[0] += bullet_speed
        if bullet[0] > WINDOW_WIDTH:
            bullets.remove(bullet)

        # 检测子弹是否击中敌人
        for enemy in enemies[:]:
            if enemy['x'] < bullet[0] < enemy['x'] + enemy_width and \
                    enemy['y'] < bullet[1] < enemy['y'] + enemy_height:
                bullets.remove(bullet)
                enemies.remove(enemy)

def spawn_enemy():
    global spawn_timer
    spawn_timer += 1
    if spawn_timer >= spawn_delay:
        spawn_timer = 0
        enemy_y = random.randint(0, WINDOW_HEIGHT - enemy_height)
        enemies.append({'x': WINDOW_WIDTH, 'y': enemy_y})

def move_enemies():
    global enemies
    for enemy in enemies[:]:
        enemy['x'] -= enemy_speed
        if enemy['x'] + enemy_width < 0:  # 敌人移出屏幕
            enemies.remove(enemy)

# 主游戏循环
running = True
while running:
    screen.fill(BLACK)
    draw_grid()

    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 鼠标左键
            bullets.append([hero_x + hero_width, hero_y + hero_height // 2])

    # 处理英雄移动
    keys_pressed = pygame.key.get_pressed()
    move_hero(keys_pressed)

    # 生成敌人
    spawn_enemy()

    # 移动敌人
    move_enemies()

    # 处理子弹
    handle_bullets()

    # 绘制英雄
    pygame.draw.rect(screen, BLUE, (hero_x, hero_y, hero_width, hero_height))

    # 绘制子弹
    for bullet in bullets:
        pygame.draw.circle(screen, YELLOW, bullet, bullet_radius)

    # 绘制敌人
    for enemy in enemies:
        pygame.draw.rect(screen, RED, (enemy['x'], enemy['y'], enemy_width, enemy_height))

    # 更新屏幕
    pygame.display.flip()

    # 帧率控制
    clock.tick(60)

# 退出 Pygame
pygame.quit()
sys.exit()

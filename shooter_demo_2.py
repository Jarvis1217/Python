import sys
import math
import random
import pygame
from pygame.math import Vector2 as V2

# -------------------------
# 配置
# -------------------------
WIDTH, HEIGHT = 960, 540
FPS = 60

# 颜色
BG_COLOR = (16, 18, 24)
PLAYER_COLOR = (235, 235, 245)
BARREL_COLOR = (160, 210, 255)
BULLET_COLOR = (255, 230, 120)
ENEMY_COLOR = (225, 70, 70)
ENEMY_OUTLINE = (255, 140, 140)
UI_COLOR = (210, 210, 210)
UI_DIM = (150, 150, 150)
HIT_FLASH = (255, 60, 60)

# 玩家外形与枪口
SQUARE_SIZE = 28
PLAYER_COLLISION_RADIUS = SQUARE_SIZE // 2  # 用于碰撞判定（简化为圆）

MUZZLE_BASE = 16     # 枪口底部离玩家中心距离
MUZZLE_LENGTH = 20   # 枪口长度（用于绘制与子弹出生点）
FIRE_COOLDOWN = 0.18 # 射速（秒/发）

# 子弹
BULLET_RADIUS = 4
BULLET_SPEED = 700.0

# 敌人
ENEMY_RADIUS_MIN = 12
ENEMY_RADIUS_MAX = 18
ENEMY_SPEED_MIN = 75.0
ENEMY_SPEED_MAX = 125.0
SPAWN_INTERVAL_START = 0.9  # 初始生成间隔
SPAWN_INTERVAL_MIN = 1      # 最小生成间隔
SPAWN_ACCEL_TIME = 90.0     # 多长时间从初始间隔过渡到最小间隔（秒）

PLAYER_MAX_HP = 3
INVULN_TIME = 1.0           # 受击后的无敌时间（秒）

# -------------------------
# 工具函数
# -------------------------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def lerp(a, b, t):
    return a + (b - a) * t

def length_safe(v: V2):
    l = v.length()
    return l if l > 1e-6 else 0.0

# -------------------------
# 实体
# -------------------------
class Bullet:
    __slots__ = ("pos", "vel", "radius")
    def __init__(self, pos: V2, vel: V2):
        self.pos = V2(pos)
        self.vel = V2(vel)
        self.radius = BULLET_RADIUS

    def update(self, dt: float):
        self.pos += self.vel * dt

    def offscreen(self):
        return (self.pos.x < -50 or self.pos.x > WIDTH + 50 or
                self.pos.y < -50 or self.pos.y > HEIGHT + 50)

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, BULLET_COLOR, (int(self.pos.x), int(self.pos.y)), self.radius)

class Enemy:
    __slots__ = ("pos", "speed", "radius")
    def __init__(self, pos: V2, speed: float, radius: int):
        self.pos = V2(pos)
        self.speed = speed
        self.radius = radius

    def update(self, dt: float, player_pos: V2):
        d = player_pos - self.pos
        l = length_safe(d)
        if l > 0:
            self.pos += d * (self.speed * dt / l)

    def draw(self, surf: pygame.Surface):
        center = (int(self.pos.x), int(self.pos.y))
        pygame.draw.circle(surf, ENEMY_COLOR, center, self.radius)
        pygame.draw.circle(surf, ENEMY_OUTLINE, center, self.radius, 2)

# -------------------------
# 敌人生成
# -------------------------
def random_spawn_pos():
    # corners: 4 个角; edges: 4 条边的随机点
    if random.random() < 0.25:  # 25% 角落
        return random.choice([
            V2(0, 0),
            V2(WIDTH, 0),
            V2(0, HEIGHT),
            V2(WIDTH, HEIGHT),
        ])
    else:
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            return V2(random.uniform(0, WIDTH), 0)
        elif side == "bottom":
            return V2(random.uniform(0, WIDTH), HEIGHT)
        elif side == "left":
            return V2(0, random.uniform(0, HEIGHT))
        else:
            return V2(WIDTH, random.uniform(0, HEIGHT))

def spawn_enemy():
    pos = random_spawn_pos()
    speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
    radius = random.randint(ENEMY_RADIUS_MIN, ENEMY_RADIUS_MAX)
    return Enemy(pos, speed, radius)

# -------------------------
# 绘制玩家小正方形与枪口
# -------------------------
def draw_player_square(surf: pygame.Surface, center: V2, color, flash=False):
    cx, cy = int(center.x), int(center.y)
    c = HIT_FLASH if flash else color
    rect = pygame.Rect(0, 0, SQUARE_SIZE, SQUARE_SIZE)
    rect.center = (cx, cy)
    pygame.draw.rect(surf, c, rect, border_radius=4)

def draw_barrel(surf: pygame.Surface, center: V2, angle: float):
    # 枪口以线段表示，始终指向鼠标
    dir_vec = V2(math.cos(angle), math.sin(angle))
    start = center + dir_vec * MUZZLE_BASE
    end = center + dir_vec * (MUZZLE_BASE + MUZZLE_LENGTH)
    pygame.draw.line(
        surf,
        BARREL_COLOR,
        (int(start.x), int(start.y)),
        (int(end.x), int(end.y)),
        8
    )
    pygame.draw.circle(surf, BARREL_COLOR, (int(end.x), int(end.y)), 4)
    return end  # 返回枪口端点，供生成子弹使用

# -------------------------
# 主游戏
# -------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Shooter_Demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    big_font = pygame.font.SysFont(None, 48)

    # 游戏状态
    player_pos = V2(WIDTH / 2, HEIGHT / 2)
    bullets: list[Bullet] = []
    enemies: list[Enemy] = []

    running = True
    mouse_down = False
    time_since_last_shot = 0.0
    spawn_timer = 0.0
    elapsed_time = 0.0

    score = 0
    hp = PLAYER_MAX_HP
    invuln = 0.0
    game_over = False

    # 预生成少量敌人
    for _ in range(3):
        enemies.append(spawn_enemy())

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                if game_over and event.key == pygame.K_r:
                    # 重开
                    bullets.clear()
                    enemies.clear()
                    score = 0
                    hp = PLAYER_MAX_HP
                    invuln = 0.0
                    game_over = False
                    time_since_last_shot = 0.0
                    spawn_timer = 0.0
                    elapsed_time = 0.0
                    for _ in range(3):
                        enemies.append(spawn_enemy())
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False

        # 逻辑更新
        mx, my = pygame.mouse.get_pos()
        aim_angle = math.atan2(my - player_pos.y, mx - player_pos.x)

        if not game_over:
            elapsed_time += dt
            time_since_last_shot += dt
            spawn_timer += dt
            invuln = max(0.0, invuln - dt)

            # 射击（点击或按住）
            if mouse_down and time_since_last_shot >= FIRE_COOLDOWN:
                dir_vec = V2(math.cos(aim_angle), math.sin(aim_angle))
                muzzle_tip = player_pos + dir_vec * (MUZZLE_BASE + MUZZLE_LENGTH)
                bullets.append(Bullet(muzzle_tip, dir_vec * BULLET_SPEED))
                time_since_last_shot = 0.0

            # 动态调节刷怪速度（随时间加快）
            # t = clamp(elapsed_time / SPAWN_ACCEL_TIME, 0.0, 1.0)
            # current_spawn_interval = lerp(SPAWN_INTERVAL_START, SPAWN_INTERVAL_MIN, t)

            current_spawn_interval = SPAWN_INTERVAL_MIN

            if spawn_timer >= current_spawn_interval:
                enemies.append(spawn_enemy())
                spawn_timer = 0.0

            # 更新子弹
            for b in bullets[:]:
                b.update(dt)
                if b.offscreen():
                    bullets.remove(b)

            # 更新敌人
            for e in enemies:
                e.update(dt, player_pos)

            # 碰撞：子弹-敌人
            for b in bullets[:]:
                for e in enemies[:]:
                    if (e.pos - b.pos).length_squared() <= (e.radius + b.radius) ** 2:
                        bullets.remove(b)
                        enemies.remove(e)
                        score += 1
                        break  # 该子弹已删除，跳出到下一颗子弹

            # 碰撞：敌人-玩家
            if invuln <= 0.0:
                for e in enemies[:]:
                    if (e.pos - player_pos).length_squared() <= (e.radius + PLAYER_COLLISION_RADIUS) ** 2:
                        hp -= 1
                        invuln = INVULN_TIME
                        enemies.remove(e)
                        if hp <= 0:
                            game_over = True
                        break

        # 绘制
        screen.fill(BG_COLOR)

        # 敌人
        for e in enemies:
            e.draw(screen)

        # 子弹
        for b in bullets:
            b.draw(screen)

        # 玩家（无敌时间闪烁）
        flash = (invuln > 0.0) and (int(invuln * 12) % 2 == 0)
        draw_player_square(screen, player_pos, PLAYER_COLOR, flash=flash)
        # 枪管（在玩家之后绘制，保证显示在上层）
        draw_barrel(screen, player_pos, aim_angle)

        # UI
        score_surf = font.render(f"Score: {score}", True, UI_COLOR)
        screen.blit(score_surf, (12, 10))

        # HP 显示
        for i in range(PLAYER_MAX_HP):
            r = 8
            x = 12 + i * 24
            y = 40
            color = UI_COLOR if i < hp else UI_DIM
            pygame.draw.circle(screen, color, (x, y), r)
            pygame.draw.circle(screen, (80, 80, 80), (x, y), r, 1)

        # 游戏结束提示
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            msg1 = big_font.render("Game Over", True, (240, 240, 240))
            msg2 = font.render("Press R to Restart, ESC to Quit", True, (200, 200, 200))
            screen.blit(msg1, msg1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 16)))
            screen.blit(msg2, msg2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
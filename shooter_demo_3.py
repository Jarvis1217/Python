import random
import pygame
from typing import List, Tuple

# ----------------------------
# 基本参数（可自行调整）
# ----------------------------
WIDTH, HEIGHT = 660, 550
FPS = 60

BG_COLOR = (18, 18, 22)
CROSS_COLOR = (0, 220, 0)
BULLET_COLOR = (255, 230, 90)       # 子弹颜色（RGB）
DISC_COLOR = (255, 120, 80)
DISC_OUTLINE = (30, 30, 35)
TEXT_COLOR = (235, 235, 235)

# 物理与难度
GRAVITY = 1200.0  # 像素/秒^2
DISC_RADIUS = 18
SPAWN_MIN = 0.8   # 最短生成间隔（秒）
SPAWN_MAX = 1.5   # 最长生成间隔（秒）
DISC_VX_RANGE = (300.0, 500.0)   # 圆盘水平初速范围
DISC_VY_RANGE = (-620.0, -420.0) # 圆盘竖直初速范围（负值代表向上抛）
DISC_SPAWN_Y_RANGE = (HEIGHT * 0.45, HEIGHT * 0.85)  # 左侧随机高度

# Z 轴“透视子弹”参数
BULLET_RADIUS = 10           # 初始屏幕半径（像素）
BULLET_SPEED_Z = 3800.0      # 子弹向屏幕内的速度（像素/秒，越大缩小越快）
FOCAL_LEN = 450.0            # 透视“焦距”（像素，越大缩小越慢）
BULLET_MIN_SCALE = 0.06      # 比例小到该阈值后结束动画
BULLET_GAMMA = 0.9           # 透明度曲线指数组，1 为线性，<1 更亮一些


class BulletZ:
    """
    视觉用“深度子弹”：固定屏幕位置 (x,y)，沿虚拟 Z 轴远离视点。
    半径与透明度按透视比例缩小/淡出，用于渲染效果，不参与飞行碰撞。
    """
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.z = 0.0
        self.alive = True
        self.scale = 1.0
        self.r = BULLET_RADIUS
        self.alpha = 255

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        self.z += BULLET_SPEED_Z * dt
        # 简化透视：scale = 1 / (1 + z / f)
        self.scale = 1.0 / (1.0 + self.z / FOCAL_LEN)
        if self.scale < BULLET_MIN_SCALE:
            self.alive = False
            return
        self.r = max(1, int(BULLET_RADIUS * self.scale))
        self.alpha = max(0, min(255, int(255 * (self.scale ** BULLET_GAMMA))))

    def draw(self, surf: pygame.Surface) -> None:
        if not self.alive or self.r <= 0 or self.alpha <= 0:
            return
        d = self.r * 2 + 4  # 留出 2px 边缘避免裁切
        tmp = pygame.Surface((d, d), pygame.SRCALPHA)

        cx = d // 2
        cy = d // 2

        # 核心亮点
        core_color = (*BULLET_COLOR, self.alpha)
        pygame.draw.circle(tmp, core_color, (cx, cy), self.r)

        # 柔和光晕（外环，透明一点）
        glow_alpha = max(0, int(self.alpha * 0.45))
        glow_r = max(self.r + 2, int(self.r * 1.35))
        pygame.draw.circle(tmp, (255, 255, 255, glow_alpha), (cx, cy), glow_r, width=2)

        surf.blit(tmp, (int(self.x - cx), int(self.y - cy)))


class Disc:
    def __init__(self) -> None:
        self.r = DISC_RADIUS
        self.x = self.r + 2  # 从左侧稍微偏内生成
        self.y = random.uniform(*DISC_SPAWN_Y_RANGE)
        self.vx = random.uniform(*DISC_VX_RANGE)
        self.vy = random.uniform(*DISC_VY_RANGE)
        self.hit = False
        self.alive = True

    def update(self, dt: float) -> Tuple[bool, bool]:
        """
        返回 (reached_right, was_hit)
        reached_right: 是否越过右侧边界
        was_hit: 是否已被击中（仅用于统计时避免重复）
        """
        self.vy += GRAVITY * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        reached_right = False
        if self.x - self.r > WIDTH:
            reached_right = True
            self.alive = False  # 到达右侧即移除
        return reached_right, self.hit

    def draw(self, surf: pygame.Surface) -> None:
        pygame.draw.circle(surf, DISC_COLOR, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(surf, DISC_OUTLINE, (int(self.x), int(self.y)), self.r, 2)


def draw_crosshair(surf: pygame.Surface, pos: Tuple[int, int]) -> None:
    x, y = pos
    arm = 12
    thick = 2
    ring_r = 18
    # 十字
    pygame.draw.line(surf, CROSS_COLOR, (x - arm, y), (x + arm, y), thick)
    pygame.draw.line(surf, CROSS_COLOR, (x, y - arm), (x, y + arm), thick)
    # 外环（装饰）
    # pygame.draw.circle(surf, (0, 140, 0), (x, y), ring_r, 1)


def hitscan_shoot(mx: int, my: int, discs: List[Disc]) -> int:
    """
    射线命中判定：点击时若准星覆盖某个圆盘，立即命中。
    返回命中数量（此处设为同时只命中一个：距离最近的那个）。
    """
    best_i = -1
    best_d2 = 1e20
    for i, d in enumerate(discs):
        if not d.alive or d.hit:
            continue
        dx = d.x - mx
        dy = d.y - my
        d2 = dx * dx + dy * dy
        if d2 <= d.r * d.r and d2 < best_d2:
            best_d2 = d2
            best_i = i

    if best_i >= 0:
        discs[best_i].hit = True
        discs[best_i].alive = False
        return 1
    return 0


def main() -> None:
    pygame.init()
    pygame.display.set_caption("shooter_game")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("simhei", 22)  # 尝试中文黑体；若缺失系统会回退

    bullets: List[BulletZ] = []
    discs: List[Disc] = []

    score = 0
    miss = 0

    # 随机生成计时器
    spawn_timer = random.uniform(SPAWN_MIN, SPAWN_MAX)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.mouse.get_focused():
                    mx, my = pygame.mouse.get_pos()
                    # 生成“向屏幕深处”的子弹动画
                    b = BulletZ(mx, my)
                    bullets.append(b)
                    # 射线命中判定（点击瞬间判定）
                    score += hitscan_shoot(mx, my, discs)

        # 生成新圆盘
        spawn_timer -= dt
        if spawn_timer <= 0:
            discs.append(Disc())
            spawn_timer = random.uniform(SPAWN_MIN, SPAWN_MAX)

        # 更新圆盘，并统计未击中到达右侧的“失误”
        still_discs: List[Disc] = []
        for d in discs:
            reached_right, was_hit = d.update(dt)
            if reached_right and not was_hit:
                miss += 1
            if d.alive:
                still_discs.append(d)
        discs = still_discs

        # 更新子弹动画
        for b in bullets:
            b.update(dt)
        bullets = [b for b in bullets if b.alive]

        # 渲染
        screen.fill(BG_COLOR)

        # 画圆盘与子弹
        for d in discs:
            d.draw(screen)
        for b in bullets:
            b.draw(screen)

        # HUD: 得分与失误
        hud = font.render(f"得分: {score}    失误: {miss}", True, TEXT_COLOR)
        screen.blit(hud, (12, 10))

        # 十字准星（鼠标在窗口内才显示，同时隐藏系统光标）
        focused = pygame.mouse.get_focused()
        pygame.mouse.set_visible(not focused)
        if focused:
            draw_crosshair(screen, pygame.mouse.get_pos())

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
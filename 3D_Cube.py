import pygame
import math
from pygame.locals import *

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Cube")

clock = pygame.time.Clock()

# 顶点
vertices = [
    [-1, -1, -1], [-1, -1,  1], [-1,  1, -1], [-1,  1,  1],
    [ 1, -1, -1], [ 1, -1,  1], [ 1,  1, -1], [ 1,  1,  1]
]

# 边
edges = [
    (0, 1), (1, 3), (3, 2), (2, 0),
    (4, 5), (5, 7), (7, 6), (6, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

# 旋转角度
angle_x, angle_y = 0, 0

# 3D 点投影
def project(point):
    fov = 500 # 视场角
    distance = 5 # 投影距离
    factor = fov / (distance + point[2])
    x = int(point[0] * factor + WIDTH // 2)
    y = int(-point[1] * factor + HEIGHT // 2)
    return (x, y)

# 绕 X 轴旋转
def rotate_x(point, angle):
    y = point[1] * math.cos(angle) - point[2] * math.sin(angle)
    z = point[1] * math.sin(angle) + point[2] * math.cos(angle)
    return [point[0], y, z]

# 绕 Y 轴旋转
def rotate_y(point, angle):
    x = point[2] * math.sin(angle) + point[0] * math.cos(angle)
    z = point[2] * math.cos(angle) - point[0] * math.sin(angle)
    return [x, point[1], z]

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # 获取鼠标移动
    mouse_dx, mouse_dy = pygame.mouse.get_rel()
    if pygame.mouse.get_pressed()[0]:
        angle_y -= mouse_dx * 0.01
        angle_x -= mouse_dy * 0.01

    screen.fill((0, 0, 0))

    # 转换和投影顶点
    transformed_vertices = []
    for vertex in vertices:
        rotated = rotate_x(vertex, angle_x)
        rotated = rotate_y(rotated, angle_y)
        transformed_vertices.append(project(rotated))

    # 绘制边
    for edge in edges:
        pygame.draw.line(screen, (255, 255, 255), transformed_vertices[edge[0]], transformed_vertices[edge[1]], 1)

    # 显示顶点坐标
    font = pygame.font.Font(None, 24)
    for i, vertex in enumerate(transformed_vertices):
        label = font.render(f"{i}: {vertex}", True, (135, 206, 235))

        if i in [0, 1, 2, 3]:
            screen.blit(label, (vertex[0] - 100, vertex[1]))
        else:
            screen.blit(label, (vertex[0] + 10, vertex[1] + 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

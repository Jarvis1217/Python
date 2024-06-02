import random
import matplotlib.pyplot as plt

def generate_maze(width, height):
    # 用墙（1）初始化网格
    maze = [[1] * (width * 2 + 1) for _ in range(height * 2 + 1)]

     # 创建一个绘图窗口和坐标轴
    fig, ax = plt.subplots()

    # 定义一个函数，用于绘制迷宫
    def draw_maze():
        # 清空坐标轴
        ax.clear()
        # 绘制迷宫，使用二值（binary）颜色映射
        ax.imshow(maze, cmap='binary')
        # 隐藏坐标轴的刻度
        ax.set_xticks([])
        ax.set_yticks([])
        # 更新图形
        plt.draw()
    
    # 定义在网格中移动的方向
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
    
    def dfs(x, y):
        # 将当前单元格标记为通道（0）
        maze[x][y] = 0
        
        # 随机打乱方向列表
        random.shuffle(directions)
        
        # 遍历所有方向
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # 检查新的坐标是否在边界内，并且是否是墙
            if 1 <= nx < height * 2 and 1 <= ny < width * 2 and maze[nx][ny] == 1:
                # 打破单元格之间的墙
                maze[x + dx // 2][y + dy // 2] = 0
                # 递归调用DFS，继续生成迷宫
                dfs(nx, ny)
    
    # 从初始单元格（1, 1）开始深度优先搜索
    dfs(1, 1)
    
    maze[1][0] = 0  # 入口
    maze[height * 2 - 1][width * 2] = 0  # 出口

    # 绘制迷宫
    draw_maze()
    # 显示图形
    plt.show()

    return maze

# 生成一个5x5的迷宫
width, height = 30, 30
maze = generate_maze(width, height)

# 打印迷宫数组
# for row in maze:
#     print(row)

# 打印迷宫
# for row in maze:
#     for j in row:
#         print(" ■ " if j == 1 else "   ", end="")
#     print()

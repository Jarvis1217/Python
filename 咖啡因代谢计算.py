def caffeine_metabolism(initial_caffeine, half_life, hours):
    caffeine_content = initial_caffeine * (0.5 ** (hours / half_life))
    return caffeine_content

# 初始咖啡因含量（mg）
initial_caffeine = 200
# 咖啡因半衰期（小时）
half_life = 5

# 每24小时观察一次咖啡因剩余量
for hour in range(0, 169):
    caffeine_content = caffeine_metabolism(initial_caffeine, half_life, hour)
    if hour % 24 == 0:
        print(f"{hour} 小时: 咖啡因含量 {round(caffeine_content, 2)}mg")

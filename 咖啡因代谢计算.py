# 初始量
initial_caffeine = 200

# 半衰期
half_life = 5

for i in range(7):
	initial_caffeine = initial_caffeine * (0.5 ** (24 / half_life))
	print(f"第{i+1}天体内咖啡因含量为: {initial_caffeine:.2f}mg")
    

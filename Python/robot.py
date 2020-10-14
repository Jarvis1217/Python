import os
import time

print("你好...")
time.sleep(2)

# 暂停三秒后自动删除
print("再见...")
time.sleep(3)

# 自动删除自身
file=os.path.realpath(__file__)
self_path = (file)
if os.path.exists(file):
    os.remove(self_path)

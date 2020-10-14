import time
import os

t=int(input("input start time:"))
os.system('cls')
for i in range(t):
    print( "\033[?25l")
    print("you have",t,"s left")
    t=t-1
    time.sleep(1)
    os.system('cls')
print("time is over!")
print("\033[?25h")

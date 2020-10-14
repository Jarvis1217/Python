import random

num_real=random.randint(1,101)
num_guess=int(input("input your guess:"))

while num_real!=num_guess:
    if num_guess<num_real:
        print("your guess is smaller")
        print("\n")
    elif num_guess>num_real:
        print("your guess is lager")
        print("\n")
    num_guess=int(input("input your guess:"))

print("your guess is right")

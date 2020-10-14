import random

def qsort(arr):
    
    if len(arr)<=1:
        return arr
    
    mid=arr[len(arr)//2]
    left=[n for n in arr if n<mid]
    middle=[n for n in arr if n==mid]
    right=[n for n in arr if n>mid]
    
    return qsort(left)+middle+qsort(right)

num=[random.randint(1,10) for i in range(15)]

print(num)
print(qsort(num))

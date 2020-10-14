import random
import itertools

# Give random number list
def Give_num():
    li=[random.randint(1,9) for i in range(4)]
    return li

# List to String
def st(num_list):
    li=[str(i) for i in num_list]
    return li

# 24 calculation
def calc_24(li):
    result=[]
    symbols=["+","-","*","/"]
    for li in itertools.permutations(li,4):
        for op in itertools.product(symbols,repeat=4):
            n=li[0]+op[0]+li[1]+op[1]+li[2]+op[2]+li[3]
            if eval(n) == 24:
                result.append(n)
            
    return result



# main()
num_list=Give_num()
print('随机数组:%s' %num_list)

num_list=st(num_list)

res=calc_24(num_list)

for i in set(res):
    print(i +'=24')

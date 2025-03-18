import itertools
import random


def Give_num():
    li = [random.randint(1, 9) for i in range(4)]
    return li


def st(num_list):
    li = [str(i) for i in num_list]
    return li


def calc_24(li):
    result = []
    symbols = ["+", "-", "*", "/"]
    for li in itertools.permutations(li, 4):
        for op in itertools.product(symbols, repeat=4):
            # 1.((A*B)*C)*D
            n1 = '(' + '(' + li[0] + op[0] + li[1] + ')' + op[1] + li[2] + ')' + op[2] + li[3]
            # 2.(A*(B*C))*D
            n2 = '(' + li[0] + op[0] + '(' + li[1] + op[1] + li[2] + ')' + ')' + op[2] + li[3]
            # 3.(A*B)*(C*D)
            n3 = '(' + li[0] + op[0] + li[1] + ')' + op[1] + '(' + li[2] + op[2] + li[3] + ')'
            # 4.A*(B*(C*D))
            n4 = li[0] + op[0] + '(' + li[1] + op[1] + '(' + li[2] + op[2] + li[3] + ')' + ')'
            # 5.A*((B*C)*D)
            n5 = li[0] + op[0] + '(' + '(' + li[1] + op[1] + li[2] + ')' + op[2] + li[3] + ')'

            try:
                if eval(n1) == 24:
                    result.append(n1)
                if eval(n2) == 24:
                    result.append(n2)
                if eval(n3) == 24:
                    result.append(n3)
                if eval(n4) == 24:
                    result.append(n4)
                if eval(n4) == 24:
                    result.append(n5)
            except ZeroDivisionError:
                pass
    return result

def Game_play():
    num_list = Give_num()
    print('随机数组:%s' % num_list)
    print('输入‘ans’查看答案...')
    if input() == 'ans':
        num_list = st(num_list)
        res = calc_24(num_list)
        if not res:
            print('未能找到答案')
        else:
            print(res[0])
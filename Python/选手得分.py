import random

# get_result
def get_result():
    grd_list.remove(max(grd_list))
    grd_list.remove(min(grd_list))
    length=len(grd_list)
    sum=0
    for i in range(length):
        sum += grd_list[i]
    
    result=sum/len(grd_list)
    return result

# main()
grd_list=[random.randint(10,100) for i in range(10)]

print("评委评分结果:")
print(grd_list)

res=get_result()
print("选手最终得分:%.2f" %res)

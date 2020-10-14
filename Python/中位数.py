num1=input().split(",")
num2=input().split(",")

num1=[int(num1[i]) for i in range(len(num1))]
num2=[int(num2[i]) for i in range(len(num2))]
leng=len(num1)+len(num2)

num1=num1+num2
num1.sort()

if leng%2==0:

    flag=leng/2
    result=(num1[int(flag)-1]+num1[int(flag)])/2

if leng%2!=0:

    flag=(leng+1)/2
    result=num1[int(flag)-1]


print("%.1f" % result)

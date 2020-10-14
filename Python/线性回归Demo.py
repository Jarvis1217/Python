import math

# calc_b
def get_b(x_list,y_list,xp,yp):
	top_left=0
	top_right=0
	dow_left=0
	dow_right=0
	length=len(x_list)
	# top_left
	for i in range(length):
		top_left +=x_list[i]*y_list[i]
	# top_right
	top_right=length*xp*yp
	# dow_left
	x_list=[i**2 for i in x_list]
	for i in range(length):
		dow_left +=x_list[i]
	# dow_right
	dow_right=xp**2*length
	
	top=top_left-top_right
	dow=dow_left-dow_right
	return top/dow

# calc_a
def get_a(yp,b,xp):
	return yp-b*xp

# calc_xp
def get_xp(x_list):
	sum=0
	for i in x_list:
		sum=sum+i
	xp=sum/len(x_list)
	return xp

# calc_yp
def get_yp(y_list):
	sum=0
	for i in y_list:
		sum=sum+i
	yp=sum/len(y_list)
	return yp

# main()

x_list=[1,2,3,4,5]
y_list=[0,2,4,6,8]

xp=get_xp(x_list)
yp=get_yp(y_list)

b=get_b(x_list,y_list,xp,yp)
a=get_a(yp,b,xp)

next_num=b*6+a

print('原数列为:')
for i in y_list:
	print(i,' ',end="")
print()

print('回归方程:y=%0.2fx+%0.2f' %(b,a))
print('下一位预测值为:%f' %next_num)

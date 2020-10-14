class Point():
    
    '''构造'''
    def _init_(self,x,y):
        self.x=x
        self.y=y
    '''获取坐标'''
    def get_point(self):
        return self.x,self.y

        
point=Point()
point.x=int(input("please input x:"))
point.y=int(input("please input y:"))
print("你输入的坐标为:",point.get_point())
    

def quick_sort(list,start,end):

    if start >= end:
        return

    mid=list[start]
    low=start
    high=end

    while low<high:
        while low<high and list[high]>=mid:
            high-=1
        list[low]=list[high]

        while low<high and list[low]<mid:
            low+=1
        list[high]=list[low]

    list[low]=mid
    quick_sort(list,low+1,end)
    quick_sort(list,start,low-1)

if __name__ == '__main__':
    list=[5,4,3,6,2,1]
    quick_sort(list,0,len(list)-1)
    print(list)
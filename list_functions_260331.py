number_list = [23,45,27,11,25,65,78]

#getIndex 함수
def getIndex(number_list, target):
    for i in range (len(number_list)):
        if number_list[i] == target:
            return i 
    return -1

#getMax 함수
def getMax(number_list):
    max_val = number_list[0]
    for num in number_list:
        if num > max_val:
            max_val = num
    return max_val

#getMin 함수
def getMin(number_list):
    min_val = number_list[0]
    for num in number_list:
        if num < min_val:
            min_val = num
    return min_val

#countGT 함수
def countGT(number_list, target):
    count = 0
    for num in number_list:
        if num > target:
            count += 1
    return count

#sumList 함수
def sumList(number_list):
    total = 0
    for num in number_list:
        total += 1
    return total

#swapList 함수
def swapList(number_list):
    number_list[:] = number_list[::-1]
    
        

print(getIndex(number_list, 25))
print(getMax(number_list))
print(getMin(number_list))
print(countGT(number_list, 42))
print(sumList(number_list))
swapList(number_list)
print(number_list)

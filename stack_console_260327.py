#전역 변수 설정
max_count = 5
stack = []

#isempty 함수
def isempty():
    return len(stack) == 0

#isfull 함수
def isfull():
    return len(stack) >= max_count

#push 함수
def push(data):
    if isfull():
        print(f"Stack이 차 있어서 더 이상 추가할 수 없습니다.")
    else:
        stack.append(data)
        print(f"현재 스택 상태 {stack}")
        
#pop 함수
def pop():
    if isempty():
        print(f"Stack이 비어 있습니다.")
    else:
        popped_data = stack.pop()
        print(f"> 가져온 데이터 : {popped_data}")
        print(f"현재 스택 상태 {stack}")
        
#peek 함수
def peek():
    if isempty():
        print(f"Stack이 비어 있습니다.")
    else:
        peek_data = stack[-1]
        print(f"> 가져온 데이터 : {peek_data}")
        print(f"현재 스택 상태 {stack}")
        
#-------함수 종료--------
        

while True:
    print("\n-----------[ 정수형 스택 연산 실습 (용량 5) ]-----------")
    print("====================================================")
    print(" 1.Push    2.Pop      3.Peek     0.Exit")
    print("====================================================")
    
    menu = input("메뉴 선택 : ")
    
    if menu == '1':
        data = int(input("데이터 입력 : "))
        push(data)
    
    elif menu == '2':
        pop()
        
    elif menu == '3':
        peek()
        
    elif menu == '0':
        print(f"--------[ 정수형 스택 연산 실습 종료]----")
        break
    
    else:
        print(f"잘못된 메뉴 번호입니다. 다시 선택해 주세요.")
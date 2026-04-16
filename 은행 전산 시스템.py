import random
import oracledb
import sys

# Oracle 연결 설정 
connection_config = {
    "user": "C##bank",
    "password": "1234",
    "dsn": "localhost:1521/FREE"
}

# 전역 변수로 로그인 세션 관리
session_user = None

def get_connection():
    try:
        return oracledb.connect(**connection_config)
    except oracledb.Error as e:
        print(f"DB 연결 오류: {e}")
        sys.exit()

import re # 정규표현식 사용을 위해 최상단에 추가 필요

def register():
    print("\n[회원가입]")
    login_id = input("아이디: ").strip()
    pw = input("비밀번호: ").strip()
    name = input("이름: ").strip()
    phone = input("연락처: ").strip()
    
    # 연락처 하이픈(-) 존재 여부 체크
    if '-' not in phone:
        print("\n[오류] 연락처에 하이픈(-)이 포함되어야 합니다.(예시:010-0000-0000)")
        return
    
    # 1. 정보 누락 체크
    if not (login_id and pw and name and phone):
        print("\n[오류] 정보가 누락되었습니다. 메인 메뉴로 돌아갑니다.")
        return 

    # 2. 아이디 제약 조건 체크 (6~16자, 한글 불가)
    # re.search('[ㄱ-ㅎ가-힣]', login_id)는 한글이 포함되었는지 확인합니다.
    if len(login_id) < 6 or len(login_id) > 16 or re.search('[ㄱ-ㅎ가-힣]', login_id):
        print("\n[오류] 아이디는 한글 불가에 최소 6자리, 최대 16자리까지 가능합니다.")
        return

    # 3. 비밀번호 제약 조건 체크 (4자 이상 요청하셨으나 로직은 6자부터 가능하게 설정)
    if len(pw) < 6:
        print("\n[오류] 비밀번호는 4자리 이상이여야 합니다.") # 요청하신 문구 그대로 출력
        return
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # 아이디 중복 확인
            cursor.execute("SELECT COUNT(*) FROM Users WHERE login_id = :1", [login_id])
            if cursor.fetchone()[0] > 0:
                print("이미 존재하는 아이디입니다. 메인 메뉴로 돌아갑니다.")
                return

            sql = "INSERT INTO Users (user_id, login_id, password, name, phone) VALUES (user_seq.NEXTVAL, :1, :2, :3, :4)"
            cursor.execute(sql, [login_id, pw, name, phone])
            conn.commit()
            print(f"\n{name}님, 회원가입이 완료되었습니다!")
    except oracledb.Error as e:
        print(f"회원가입 중 오류 발생: {e}")

def login():
    global session_user
    login_id = input("아이디: ")
    pw = input("비밀번호: ")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        sql = "SELECT user_id FROM Users WHERE login_id = :1 AND password = :2"
        cursor.execute(sql, [login_id, pw])
        result = cursor.fetchone()
        
        if result:
            session_user = result[0]
            print(f"\n환영합니다! {login_id}고객님")
            bank_menu()
        else:
            print("아이디 또는 비밀번호가 틀립니다.")

def create_account():
    print("\n[내 계좌 생성]")
    part1 = "".join([str(random.randint(0, 9)) for _ in range(6)])
    part2 = "".join([str(random.randint(0, 9)) for _ in range(2)])
    part3 = "".join([str(random.randint(0, 9)) for _ in range(6)])
    new_acc_num = f"{part1}-{part2}-{part3}"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Accounts WHERE account_number = :1", [new_acc_num])
        if cursor.fetchone()[0] > 0:
            return create_account()

        try:
            sql = "INSERT INTO Accounts (account_number, user_id, balance) VALUES (:1, :2, 0)"
            cursor.execute(sql, [new_acc_num, session_user])
            conn.commit()
            print(f"새 계좌 생성 완료! [{new_acc_num}]")
        except oracledb.Error as e:
            print(f"오류 발생: {e}")
            
def check_balance():
    print("\n[내 계좌 조회]")
    with get_connection() as conn:
        cursor = conn.cursor()
        # 현재 로그인한 사용자의 모든 계좌와 잔액을 조회
        sql = "SELECT account_number, balance FROM Accounts WHERE user_id = :1"
        cursor.execute(sql, [session_user])
        accounts = cursor.fetchall()
        
        if accounts:
            print(f"{'계좌번호':<20} | {'잔액':>15}")
            print("-" * 40)
            for acc_num, balance in accounts:
                print(f"{acc_num:<20} | {balance:>15,d}원")
        else:
            print("보유하신 계좌가 없습니다.")

def deposit():
    print("\n[입금]")
    acc_num = input("입금할 계좌번호: ").strip()
    amount_str = input("금액: ").strip()
    
    if not (acc_num and amount_str):
        print("\n잘못입력되었습니다 다시 입력하세요")
        return # 은행 메뉴로 복귀

    amount = int(amount_str)
    
    # 100원 미만 체크 시 즉시 메뉴로 복귀
    if amount < 100:
        print("\n[오류] 입금은 100원부터 가능합니다. 은행 메뉴로 돌아갑니다.")
        return 

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # 계좌 존재 확인
            cursor.execute("SELECT COUNT(*) FROM Accounts WHERE account_number = :1", [acc_num])
            if cursor.fetchone()[0] == 0:
                print(f"\n[오류] 존재하지 않는 계좌번호입니다.")
                return 
            
            cursor.execute("UPDATE Accounts SET balance = balance + :1 WHERE account_number = :2", [amount, acc_num])
            cursor.execute("INSERT INTO Transactions (tx_id, to_account, amount, type) VALUES (tx_seq.NEXTVAL, :1, :2, '입금')", [acc_num, amount])
            conn.commit()
            print(f"{amount:,d}원 입금이 완료되었습니다!")
    except oracledb.Error as e:
        print(f"오류 발생: {e}")

def withdraw():
    print("\n[출금]")
    acc_num = input("출금할 내 계좌번호: ").strip()
    amount_str = input("출금 금액: ").strip()
    
    if not (acc_num and amount_str):
        print("\n잘못입력되었습니다 다시 입력하세요")
        return

    amount = int(amount_str)
    
    # 100원 미만 체크 시 즉시 메뉴로 복귀
    if amount < 100:
        print("\n[오류] 출금은 100원부터 가능합니다. 은행 메뉴로 돌아갑니다.")
        return

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM Accounts WHERE account_number = :1 AND user_id = :2", [acc_num, session_user])
            row = cursor.fetchone()
            
            if not row:
                print("\n[오류] 계좌 정보를 확인해주세요.")
                return

            current_balance = row[0]
            if amount > current_balance:
                print("\n[오류] 출금하는 금액이 잔액보다 많습니다.")
                return

            cursor.execute("UPDATE Accounts SET balance = balance - :1 WHERE account_number = :2", [amount, acc_num])
            cursor.execute("INSERT INTO Transactions (tx_id, from_account, amount, type) VALUES (tx_seq.NEXTVAL, :1, :2, '출금')", [acc_num, amount])
            conn.commit()
            print(f"{amount:,d}원 출금이 완료되었습니다.")
    except oracledb.Error as e:
        print(f"오류 발생: {e}")

def transfer():
    print("\n[계좌이체]")
    from_acc = input("내 계좌번호: ").strip()
    to_acc = input("상대 계좌번호: ").strip()
    amount_str = input("이체 금액: ").strip()
    
    if not (from_acc and to_acc and amount_str):
        print("\n정보가 누락되었습니다. 다시 입력하세요.")
        return

    amount = int(amount_str)
    
    # 100원 미만 체크 시 즉시 메뉴로 복귀
    if amount < 100:
        print("\n[오류] 이체는 100원부터 가능합니다. 은행 메뉴로 돌아갑니다.")
        return

    if from_acc == to_acc:
        print("\n[오류] 동일한 계좌로는 이체할 수 없습니다.")
        return

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # 내 계좌 확인
            cursor.execute("SELECT balance FROM Accounts WHERE account_number = :1 AND user_id = :2", [from_acc, session_user])
            row = cursor.fetchone()
            if not row:
                print(f"\n[오류] 내 계좌 정보를 확인해주세요.")
                return
            
            if amount > row[0]:
                print("\n[오류] 잔액이 부족합니다.")
                return

            # 상대 계좌 확인
            cursor.execute("SELECT COUNT(*) FROM Accounts WHERE account_number = :1", [to_acc])
            if cursor.fetchone()[0] == 0:
                print(f"\n[오류] 상대방 계좌가 존재하지 않습니다.")
                return

            cursor.execute("UPDATE Accounts SET balance = balance - :1 WHERE account_number = :2", [amount, from_acc])
            cursor.execute("UPDATE Accounts SET balance = balance + :1 WHERE account_number = :2", [amount, to_acc])
            cursor.execute("INSERT INTO Transactions (tx_id, from_account, to_account, amount, type) VALUES (tx_seq.NEXTVAL, :1, :2, :3, '이체')", [from_acc, to_acc, amount])
            conn.commit()
            print(f"\n이체 완료! ({amount:,d}원)")
    except oracledb.Error as e:
        print(f"오류 발생: {e}")
        
        
def view_transactions():
    print("\n[거래내역 조회]")
    acc_num = input("조회할 내 계좌번호: ").strip()
    
    if not acc_num:
        print("계좌번호를 입력해야 합니다.")
        return

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # 쿼리 실행 전 계좌 존재 여부 확인 (생략 가능)
            
            # SQL 문 실행
            # 주의: 테이블 생성 시 컬럼명이 tx_date가 맞는지 확인하세요.
            sql = """
                SELECT tx_id, from_account, to_account, amount, type, tx_date 
                FROM Transactions 
                WHERE from_account = :1 OR to_account = :1
                ORDER BY tx_date DESC
            """
            cursor.execute(sql, [acc_num, acc_num])
            rows = cursor.fetchall()
            
            if rows:
                print(f"\n{'ID':<5} | {'보낸계좌':<15} | {'받은계좌':<15} | {'금액':>12} | {'유형':<6} | {'거래일시'}")
                print("-" * 85)
                for tid, fr, to, amt, t_type, t_date in rows:
                    fr_display = fr if fr else "외부(입금)"
                    to_display = to if to else "외부(출금)"
                    # 금액에 천단위 콤마 추가
                    amt_display = format(int(amt), ',')
                    print(f"{tid:<5} | {fr_display:<15} | {to_display:<15} | {amt_display:>12} | {t_type:<6} | {t_date}")
            else:
                print("해당 계좌의 거래 내역이 존재하지 않습니다.")
                
    except oracledb.Error as e:
        # 구체적인 오라클 에러 메시지(ORA-XXXXX)를 출력합니다.
        print(f"\n 데이터베이스 오류 발생: {e}")
    except Exception as e:
        print(f"\n 기타 오류 발생: {e}")

def bank_menu():
    global session_user
    while session_user:
        print("\n--- 은행 메뉴 ---")
        print("1.계좌생성 2.계좌조회 3.입금 4.출금 5.이체 6.거래내역 7.로그아웃")
        choice = input("선택: ")
        
        if choice == '1': create_account()
        elif choice == '2': check_balance()
        elif choice == '3': deposit()
        elif choice == '4': withdraw()         # 출금 추가
        elif choice == '5': transfer()
        elif choice == '6': view_transactions() # 거래내역 조회 추가
        elif choice == '7': 
            session_user = None
            print("로그아웃 되었습니다.")

def main_menu():
    while True:
        print("\n--- 메인 메뉴 ---")
        print("1. 회원가입  2. 로그인  3. 종료")
        choice = input("선택: ")
        
        if choice == '1': register()
        elif choice == '2': login()
        elif choice == '3': 
            print("\n종료 되었습니다 안녕히 가십시오.") # 종료 인사 추가
            sys.exit() # 프로그램 완전 종료

if __name__ == "__main__":
    main_menu()
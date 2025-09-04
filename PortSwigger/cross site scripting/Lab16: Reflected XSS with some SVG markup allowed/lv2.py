import requests
import os
from typing import List

session = requests.Session()

BASE_URL = "https://0a0b008204fb3a8b80853af300a20058.h1-web-security-academy.net/"

def get_wordlist():
    dir_path = os.path.dirname(os.path.realpath(__file__))  # 取得當前檔案資料夾
    file_path = os.path.join(dir_path, "wordlist.txt")
    
    with open(file_path, "r", encoding="utf-8") as f:
        word_list = [line.strip() for line in f]

    print(word_list)
    return word_list

def get_useful_tags(tag_word_list:List[str])->List[str]:
    result = set()
    for word in tag_word_list:
        payload=f"<{word}>"
        params = {
            "search":payload
        }
        response = session.get(BASE_URL,params=params, timeout=10)
        if response.status_code==200:
            result.add(word)

    return list(result)


def main():

    word_list = get_wordlist()
    useful_tags =  get_useful_tags(word_list)
    print(useful_tags)

       
if __name__=="__main__":
    main()
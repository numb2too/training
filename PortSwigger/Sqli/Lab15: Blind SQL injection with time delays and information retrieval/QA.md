為什麽encode_string1不等於str?


import urllib.parse

# 原始字串
str = "'%3BSELECT+CASE+WHEN+(1=1)+THEN+pg_sleep(9)+ELSE+pg_sleep(0)+END--"

# URL 解碼
decoded_string = urllib.parse.unquote(str)

# URL 加密
encode_string = urllib.parse.quote(str)

print(f"原始字串：{str}")
print(f"解碼後：{decoded_string}")
print(f"加密後：{encode_string}")


str1 = "';SELECT+CASE+WHEN+(1=1)+THEN+pg_sleep(9)+ELSE+pg_sleep(0)+END--"
# URL 解碼
decoded_string1 = urllib.parse.unquote(str1)

# URL 加密
encode_string1 = urllib.parse.quote(str1)

print(f"原始字串：{str1}")
print(f"解碼後：{decoded_string1}")
print(f"加密後：{encode_string1}")
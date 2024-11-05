from requests import get
id = input("id=")
for i in range(1001):
    get(f"http://127.0.0.1:5468/cmd=put&id={id}&data=massage {i}")
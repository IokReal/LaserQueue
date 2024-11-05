import socket

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#soc.connect(("192.168.0.141", 5468))
soc.connect(("127.0.0.1", 5468))
id = input("id=")
a = 100
while a:
    soc.send(f"cmd=give&id={id}".encode("1251"))
    a = soc.recv(1024).decode("1251")
    input(str(len(a))+ " " + a)
soc.close()
exit(0)
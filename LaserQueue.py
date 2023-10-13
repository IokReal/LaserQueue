from multiprocessing import Process 
import socket 

def main():
    print(__file__.split('\\')[-1].split('/')[-1].split('.')[:-1][0] + '.ini')
    settings = {}
    for i in open(__file__.split('\\')[-1].split('/')[-1].split('.')[:-1][0] + '.ini').read().split('\n'):
        i = i.split("#")[0]
        settings[i.split("=")[0]] = i.split("=")[1]

    serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_socket.bind((settings['address'], int(settings['port'])))
    serv_socket.listen()
    
    # Создаем два процесса
    print("Готово")
    while True:
        conn, address = serv_socket.accept()
        print("Conect to:", address)
        Process(target=client, args=(conn,)).start()


def client(conn):
    data = conn.recv(1024)
    
    method, path, _ = data.split("\n")[0].split()

    if method == "GET":
        a = f"""\
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 2
Connection: close

OK
""".encode()
        conn.sendall(a)
        conn.shutdown(socket.SHUT_RDWR)
        #conn.close()
        if path == "/favicon.ico"

if __name__ == '__main__': main()
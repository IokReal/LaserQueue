from multiprocessing import Process, Manager, Lock
import socket 
from time import sleep
from urllib.parse import unquote

lock = Lock()

OK = """HTTP/1.1 200 OK
Content-Type: text/html
Connection: close
Status Code: 200

OK
""".encode()

def main():
    man = Manager()
    update_list = man.list()
    queue = man.dict()

    queue["0000"] = ["test message"]
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
        Process(target=client, args=(conn, queue, update_list)).start()

def update(update_list):
    for i in range(len(list(update_list))):
        try:
            update_list[i].getpeername()
            update_list[i].send("200".encode())
        except:
            update_list[i] = 1
    while (1 in update_list):
        update_list.remove(1)
    print("update_list:", *update_list, sep="\n    ")


def client(conn, queue, update_list):
    match_of_empty = 5
    try:
        while True:
            prinyt = unquote(conn.recv(2048).decode())

            if len(prinyt) < 3:
                if match_of_empty:
                    print("empty", match_of_empty)
                    match_of_empty -= 1
                    continue
                conn.shutdown(socket.SHUT_RDWR)
                sleep(2)
                conn.close()
                return

            if prinyt.split("\r\n")[0].split(' ')[0] == "GET": 
                prinyt = prinyt.split("\r\n")
                prinyt = prinyt[0]
                prinyt = prinyt.split(' ')
                prinyt = " ".join(prinyt[1:-1:])
                prinyt = prinyt.split('/')
                prinyt = "/".join(prinyt[1::])
                if prinyt[0] == "?":
                    prinyt = prinyt[1::]
            print("в итоге преобразовано в:", prinyt, end='', sep='')
            
            if prinyt == 'favicon.ico':
                print(" попытка получить иконку")
                conn.sendall(OK)
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
                return
            else:
                print()
            
            try:
                out = {}
                #prinyt = prinyt.split('&data=')
                #out = {"data": prinyt[-1]}
                #prinyt = prinyt[0]
                for i in prinyt.split('&'):
                    y = i.split('=')
                    out[y[0].lower()] = y[1]
                
                prinyt = out.copy()
            except IndexError as err:
                print('error:', KeyError(err))
            
            if prinyt["cmd"].lower() == "give":
                if prinyt["id"] not in queue.copy().keys():
                    conn.sendall('   '.encode("1251"))
                    continue
                if len(queue[prinyt["id"]]) == 0:
                    conn.sendall('   '.encode("1251"))
                else:
                    out = queue[prinyt["id"]][0]
                    with lock:
                        queue[prinyt["id"]] = queue[prinyt["id"]][1::]
                    conn.sendall(out.encode("1251"))
                update(update_list)
                continue

            if prinyt["cmd"].lower() == "put":
                if prinyt["id"] not in queue.keys():
                    queue[prinyt["id"]] = []
                queue[prinyt["id"]] = queue[prinyt["id"]] + [prinyt["data"]]
                print("queue:", queue)
                update(update_list)
                
                conn.sendall(OK)
                conn.shutdown(socket.SHUT_RDWR)
                sleep(2)
                conn.close()
                return

            if prinyt["cmd"].lower() == 'auto_update':
                update_list.append(conn)
                update(update_list)
                return

            if prinyt["cmd"].lower() == "clear":
                queue[prinyt["id"]] = []
                conn.sendall(OK)
                conn.shutdown(socket.SHUT_RDWR)
                sleep(2)
                conn.close()
                update(update_list)
                return

            if prinyt["cmd"].lower() == "vc":
                queue = queue.copy()
                sleep(0.1)
                try:
                    if len(queue.keys()) == 0:
                        conn.send("message\nlist is emoty".encode("utf-8"))
                    for g in queue.keys():
                        for i in queue[g]:
                            a = g + "\n" + i
                            conn.send(a.encode("utf-8")) 
                            conn.recv(100)
                except Exception as err:
                    print(err)
                conn.shutdown(socket.SHUT_RDWR)
                sleep(2)
                conn.close()
                return
    except Exception:
        try:
            conn.shutdown(socket.SHUT_RDWR)
            sleep(2)
            conn.close()   
        except Exception:
            pass


if __name__ == '__main__': main()
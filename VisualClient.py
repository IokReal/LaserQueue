import socket
from time import sleep
from multiprocessing import Process, Manager

import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic, QtWidgets

class MyWindow(QMainWindow):
    def __init__(self, queue, settings):
        self.settings = settings
        self.queue = queue
        super().__init__()
        uic.loadUi((__file__.split('\\')[-1].split('/')[-1].split('.')[:-1][0] + '.ui'), self)
        self.pushButton_3.clicked.connect(self.clear)
        self.comboBox.currentIndexChanged.connect(self.update_list)
    
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()

    def clear(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((self.settings['address'], int(self.settings['port'])))
        id = self.comboBox.currentText()
        soc.sendall(f'cmd=clear&id={id}'.encode())

    def recurring_timer(self):
        self.update()

    def resizeEvent(self, event):
        self.gridLayoutWidget.setGeometry(0, 0, self.size().width() - 10, self.size().height() - 20)

    def update_list(self):
        try:
            a = dict(self.queue)
            self.listWidget.clear()
            self.listWidget.addItems(a[self.comboBox.currentText()])
        except:
            pass

    def update(self):
        a = dict(self.queue)
        print(a["editeng"])
        if a["editeng"] == False:
            i = int(self.comboBox.currentIndex())
            self.comboBox.clear()
            self.comboBox.addItems(a["list_of_print"])
            self.comboBox.setCurrentIndex(i)
            self.update_list()
        
        
            

class update:
    def __init__(self, settings, queue):
        self.settings = settings
        self.queue = queue
    def demon(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((self.settings['address'], int(self.settings['port'])))
        soc.sendall('cmd=auto_update'.encode())
        while soc.recv(100):
            self.run()

    def run(self):

        self.queue["editeng"] = True

        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((self.settings['address'], int(self.settings['port'])))
        soc.sendall("cmd=vc".encode())
        queue = dict(self.queue.copy())
        
        for g in queue.keys():
            self.queue[g] = []
        while True:
            data = soc.recv(2048).decode("utf-8").split("\n")
            if len(data) == 1:
                break
            soc.sendall("5".encode())
            if data[0] not in self.queue.keys():
                self.queue[data[0]] = []
            self.queue[data[0]] = self.queue[data[0]] + [data[1]]
        a = list(self.queue.keys())
        a.remove("editeng")
        a.remove("list_of_print")
        self.queue["list_of_print"] = a

        self.queue["editeng"] = False

        soc.shutdown(socket.SHUT_RDWR)
        sleep(2)
        soc.close()
        

def clear(id):
    settings={}
    for i in open(__file__.split('\\')[-1].split('/')[-1].split('.')[:-1][0] + '.ini').read().split('\n'):
        i = i.split("#")[0] + "=1"
        settings[i.split("=")[0]] = i.split("=")[1]

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((settings['address'], int(settings['port'])))

    soc.send(f"cmd=clear&id={id}".encode())


def main():
    man = Manager()
    queue = man.dict()
    queue["list_of_print"]=[]
    queue["editeng"] = False

    settings = {}
    for i in open(__file__.split('\\')[-1].split('/')[-1].split('.')[:-1][0] + '.ini').read().split('\n'):
        i = i.split("#")[0]
        settings[i.split("=")[0]] = i.split("=")[1]
    
    app = QApplication(sys.argv)
    window = MyWindow(queue, settings)
    window.setWindowTitle(f"{settings['address']}:{settings['port']}")
    
    update_per = update(settings, queue) 
    update_proc = Process(target=update_per.demon)
    update_proc.start()    

    a = 0
    try:
        window.show()
        a = app.exec_()
    except:
        pass
    update_proc.terminate()
    sys.exit(a)

if __name__ == '__main__': main()

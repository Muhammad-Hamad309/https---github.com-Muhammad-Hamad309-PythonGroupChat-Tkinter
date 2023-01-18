import socket
import threading
import queue
import json
import time
import os
import os.path
import sys

IP = '127.0.0.1'
PORT = 50007
queue = queue.Queue()                   # client
users = []                              # [conn, user, addr]
lock = threading.Lock()                 # multitreading lock

# client user list


def onlines():
    online = []
    for i in range(len(users)):
        online.append(users[i][1])
    return online


class ChatServer(threading.Thread):
    global users, queue, lock

    def __init__(self, port):
        threading.Thread.__init__(self)
        # self.setDaemon(True)
        self.ADDR = ('', port)
        # self.PORT = port
        os.chdir(sys.path[0])
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.conn = None
        # self.addr = None

    # client
    def tcp_connect(self, conn, addr):
        #username
        user = conn.recv(1024)
        user = user.decode()

        # user listverification (no multiple same users)
        for i in range(len(users)):
            if user == users[i][1]:
                print('User already exist')
                user = '' + user + '_2'

        if user == 'no':
            user = addr[0] + ':' + str(addr[1])
        users.append((conn, user, addr))
        # Print new username
        print(' New connection:', addr, ':', user, end='')
        # refresh user list
        d = onlines()
        self.recv(d, addr)
        try:
            while True:
                data = conn.recv(1024)
                data = data.decode()
                self.recv(data, addr)
            conn.close()
        except:
            print(user + ' Connection lose')
            # 把離開聊天室的從user list中移除
            self.delUsers(conn, addr)
            conn.close()

    # 刪除user
    def delUsers(self, conn, addr):
        a = 0
        for i in users:
            if i[0] == conn:
                users.pop(a)
                print(' Remaining online users: ',
                      end='')
                d = onlines()
                self.recv(d, addr)
                # print
                print(d)
                break
            a += 1

    # ip, data, addrqueue
    def recv(self, data, addr):
        lock.acquire()
        try:
            queue.put((addr, data))
        finally:
            lock.release()

    # queue
    def sendData(self):
        while True:
            if not queue.empty():
                data = ''
                # queue
                message = queue.get()
                #string
                if isinstance(message[1], str):
                    for i in range(len(users)):
                        # user[i][1], users[i][2]addr
                        for j in range(len(users)):

                            if message[0] == users[j][2]:
                                print(
                                    ' this: message is from user[{}]'.format(j))
                                data = ' ' + users[j][1] + '：' + message[1]
                                break
                        users[i][0].send(data.encode())
                # data = data.split(':;')[0]
                if isinstance(message[1], list):  # 同上
                    #list
                    data = json.dumps(message[1])
                    for i in range(len(users)):
                        try:
                            users[i][0].send(data.encode())
                        except:
                            pass

    def run(self):

        self.s.bind(self.ADDR)
        self.s.listen(5)
        print('Chat server starts running...')
        q = threading.Thread(target=self.sendData)
        q.start()
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()


if __name__ == '__main__':
    cserver = ChatServer(PORT)
    cserver.start()

    while True:
        time.sleep(1)
        if not cserver.is_alive():
            print("Chat connection lost...")
            sys.exit(0)

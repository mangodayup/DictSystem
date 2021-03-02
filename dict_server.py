"""
通信协议 LOG 登录
        REG 注册
        QUIT 退出
"""
import sys
from select import select
from socket import *
from time import sleep
import hashlib

import pymysql


class ServerController:
    def __init__(self):
        self.__dict = DictDB()

    def handle(self, connfd):
        # 接受客户端
        print("开始接收……")
        request = connfd.recv(1024)
        print("接收到:", request.decode())
        if not request:
            DictServer.rlist.remove(connfd)
            connfd.close()
        self.send_response(request, connfd)

    def send_response(self, request, connfd):


        info = request.decode().split(" ", 2)
        if info[0] == "LOG":
            self.__do_login(info[1], info[2],connfd)
        elif info[0] == "REG":
            self.__do_register(info[1], info[2],connfd)
        elif info[0] == "QUIT":
            self.__quit(connfd)
        elif info[0] == "FIND":
            self.__do_find_words(info[1], info[2],connfd)
        elif info[0] == "HISTORY":
            self.__do_view_history(info[1],connfd)


    def __do_register(self, name, passwd, connfd):
        if self.__dict.register(name,passwd):
            connfd.send(b"OK")
        else:
            connfd.send(b"FAIL")

    def __do_login(self, name, passwd, connfd):
        if self.__dict.login(name, passwd):
            connfd.send(b"OK")
        else:
            connfd.send(b"FAIL")

    def __do_find_words(self, word,name, connfd):
        mean = self.__dict.find_word(word, name)
        connfd.send(mean.encode())

    def __do_view_history(self, name,connfd):
        # data--> ((name,word,time),())
        data = self.__dict.view_history(name)
        for row in data:
            msg = "%s    %s    %s" % row
            connfd.send(msg.encode())
            sleep(0.1)
        connfd.send(b"##")

    def __quit(self,connfd):
        self.__dict.rlist.remove(connfd)
        connfd.close()
        sys.exit("客户端已退出……")


class DictServer:
    rlist = []
    def __init__(self, host="0.0.0.0", port=8888):
        self.host = host
        self.port = port
        self.address = (host, port)
        self.__sock = self.__create_socket()

        self.__controller = ServerController()

    def __create_socket(self):
        sock = socket()
        sock.bind(self.address)
        sock.setblocking(False)
        return sock

    def start(self):
        self.__sock.listen(5)
        print("Listen the port %d" % self.port)
        self.rlist.append(self.__sock)
        n = 1
        while True:
            print("第", n, "次监控……")
            n += 1
            rs, ws, xs = select(self.rlist, [], [])
            for r in rs:
                if r is self.__sock:
                    self.__connect()  # 处理客户端链接
                else:
                    try:
                        self.__controller.handle(r)  # 处理客户端请求
                    except Exception as e:
                        print("出现了错误:", e)


    def __connect(self):
        connfd, addr = self.__sock.accept()
        connfd.setblocking(False)
        print("Connect from", addr)
        self.rlist.append(connfd)


class DictDB:
    def __init__(self):
        self.kwargs = {
            "user": "root",
            "password": "123456",
            "database": "dict",
            "charset": "utf8"
        }
        self.__connect()

    def hash_encrytion(self,passwd):
        hash = hashlib.sha256(b"#*)^#")
        hash.update(passwd.encode())
        return hash.hexdigest()

    # 完成连接数据库
    def __connect(self):
        self.db = pymysql.connect(**self.kwargs)
        self.cur = self.db.cursor()

    # 关闭
    def close(self):
        self.cur.close()
        self.db.close()

    # 插入历史记录
    def insert_history(self, word,name):
        sql = "select id from user where binary user=%s;"
        self.cur.execute(sql, [name])
        id = self.cur.fetchone()[0]  # 用户id
        try:
            sql = "insert into history (word,user_id) values (%s,%s);"
            self.cur.execute(sql, [word, id])
            self.db.commit()
        except:
            self.db.rollback()

    # 插入用户信息
    def insert_user(self, name, passw):
        passw = self.hash_encrytion(passw)
        try:
            sql = "insert into user (user,password) values (%s,%s);"
            self.cur.execute(sql, (name, passw))
            self.db.commit()
            return True
        except:
            self.db.rollback()

    #查看历史记录
    def view_history(self, name):
        sql = "select user,word,time " \
              "from user left join history " \
              "on user.id=history.user_id " \
              "where user=%s " \
              "order by time desc " \
              "limit 10;"
        self.cur.execute(sql, [name])
        log = self.cur.fetchall()
        if log:
            return log
        else:
            return "Not Found"

    def register(self, name, passw):
        sql_select = "select user from user;"
        self.cur.execute(sql_select)
        all = self.cur.fetchall()
        for item in all:
            if item[0] == name:
                return False
        return self.insert_user(name, passw)

    def login(self, name, passw):
        passw =  self.hash_encrytion(passw)
        sql = "select user from user where binary user=%s and binary password=%s"
        self.cur.execute(sql,[name,passw])
        one = self.cur.fetchone()
        if one:
            return True
        else:
            return False
    def find_word(self, word, name):
        sql = "select mean from words where word=%s;"
        self.cur.execute(sql, [word])
        mean = self.cur.fetchone()  # (mean,) None
        self.insert_history(word,name)
        if mean:
            print(mean[0])
            return mean[0]
        else:
            return "Not Found"


if __name__ == '__main__':
    dict_server = DictServer(host="0.0.0.0", port=8880)
    dict_server.start()

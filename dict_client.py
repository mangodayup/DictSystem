import sys
from socket import *



class ClientView:
    ADDR = ("127.0.0.1",8880)
    def __init__(self):
        self.__sock = self.__connect()
        self.__controller = ClientController()

    def __connect(self):
        sock = socket()
        sock.connect(self.ADDR)
        return sock

    def __show_items(self):
        print("**********欢迎使用电子词典**********")
        print("""
             1. 登录
             2. 注册
             3. 退出
             """)
        print("*********************************")

    def __select_items(self):
        selection = input("请输入您的选项:")
        status = ""
        flag = 0
        if selection =="1":
            while not status:
                status = self.__controller.login(self.__sock)
            if status == -1:
                return
            self.main2(status)
        elif selection =="2":
            while not flag:
                flag = self.__controller.register(self.__sock)
        elif selection == "3":
            self.__controller.quit(self.__sock)
            self.__sock.close()
        else:
            print("您的输入有误!请重新输入!")
            self.__select_items()


    def __show_items2(self):
        print("**********欢迎使用电子词典**********")
        print("""
             1. 查询单词
             2. 历史记录
             3. 注销账户
             """)
        print("*********************************")


    def __select_items2(self, name):
        selection = input("请输入您的选项:")
        if selection == "1":
            self.__controller.find_words(self.__sock, name)
        elif selection == "2":
            self.__controller.view_history(self.__sock,name)
        elif selection == "3":
            self.main()
        else:
            print("您的输入有误!请重新输入!")
            self.__select_items2()

    def main(self):
        while True:
            self.__show_items()
            self.__select_items()

    def main2(self,name):
        while True:
            self.__show_items2()
            self.__select_items2(name)


class ClientController:
    def __init__(self):
        pass

    def login(self,sock):
        mark = "LOG "
        name = input("请输入您的用户名:(输入##返回上一层)")
        if name == "##":
            return -1
        password = input("请输入您的密码:")

        if " " in name or " " in password:
            print("用户名或密码不能有空格,请重新输入！")
            return
        if not name or not password:
            print("用户名或密码不能为空,请重新输入！")
            return
        msg = mark + name + " " + password
        sock.send(msg.encode())
        response = sock.recv(128)
        if response == b"OK":
            print("恭喜您登录成功！")
            return name
        else:
            print("不好意思，您输入的用户名或者密码有误！请重新输入！")
            return

    def register(self,sock):
        mark = "REG "
        name = input("请输入您的用户名:")
        password = input("请输入您的密码:")
        if " " in name or " " in password:
            print("用户名或密码不能有空格,请重新输入！")
            return
        if not name or not password:
            print("用户名或密码不能为空,请重新输入！")
            return
        msg = mark + name + " " + password
        sock.send(msg.encode())
        response = sock.recv(128)
        if response == b"OK":
            print("恭喜您注册成功！")
            return 1
        else:
            print("不好意思，用户名已存在！请重新输入！")
            return 0

    def quit(self,sock):
        mark = "QUIT "
        sock.send(mark.encode())
        sys.exit("退出成功!")

    def find_words(self, sock, name ):
        mark = "FIND "
        word = input("请输入要查询的单词:")
        msg = mark + word+" "+name
        print("发送给服务端的msg为:",msg)
        sock.send(msg.encode())
        response = sock.recv(1024*10)
        print("其解释为:",response.decode())

    def view_history(self, sock, name):
        mark = "HISTORY "
        msg = mark+name
        sock.send(msg.encode())
        while True:
            data = sock.recv(1024)
            if data == b"##":
                break
            print(data.decode())



if __name__ == '__main__':
    view = ClientView()
    view.main()
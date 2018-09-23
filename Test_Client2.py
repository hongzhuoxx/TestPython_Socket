import socket
import time
import struct
import json
import threading

host = "127.0.0.1"
port = 7654

ADDR = (host, port)

client = socket.socket()


def recMsg():
    print("开始信息接受")
    while True:
        print(client.recv(1024).decode(encoding='utf8'))


if __name__ == '__main__':
    
    client.connect(ADDR)

    # 正常数据包定义
    ver = 1
    body = json.dumps(dict(hello="world"))
    print(body)
    cmd = 101
    header = [ver, body.__len__(), cmd]
    headPack = struct.pack("!3I", *header)
    sendData1 = headPack+body.encode()
  
    # 正常数据包
    client.send(sendData1)

    server_thread = threading.Thread(target=recMsg)
    server_thread.daemon = True
    server_thread.start()

        # 主线程逻辑
    while True:
        cmd = input("""--------------------------
输入1:给指定客户端发送消息
输入2:关闭服务端
""")
        if cmd == '1':
            print("--------------------------")
            imsg = input("请输入消息")

            # 正常数据包定义
            ver = 1
            body = json.dumps(dict(Msg=imsg))
            print(body)
            cmd = 101
            header = [ver, body.__len__(), cmd]
            headPack = struct.pack("!3I", *header)
            sendData1 = headPack+body.encode()
        
            # 正常数据包
            client.send(sendData1)

        elif cmd == '2':
            client.close()
            exit()
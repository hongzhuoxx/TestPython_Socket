import socketserver
import struct
import threading


#主机地址
HOST='127.0.0.1'
#主机端口
PORT=7654

#连接池
g_conn_pool = []


class ZxServer(socketserver.BaseRequestHandler):

    #缓冲区
    DataBuffer=bytes()
    #头部长度
    HeaderSize=12
    #数据包计数器
    sn=0


    def setup(self):
        self.request.sendall("连接服务器成功!".encode(encoding='utf8'))
        # 加入连接池
        g_conn_pool.append(self.request)


    def finish(self):
        print("清除了这个客户端。")
 
    def remove(self):
        print("有一个客户端掉线了。")
        g_conn_pool.remove(self.request)


    def dataHandle(self,headPack, body):
        self.sn +=1
        print ("LOG________第%s个数据包" %self.sn)
        print("LOG________版本号:%s, 内容长度:%s, 命令:%s" % headPack)
        print(body.decode())
        print("")

    def handle(self):

        try:
            conn=self.request
            zState=True

            while zState:
                data = conn.recv(1024)
                if data:
                    # 把数据存入缓冲区，类似于push数据
                    self.DataBuffer += data
                    while True:
                        if len(self.DataBuffer) < self.HeaderSize:
                            print("LOG________数据包（%s Byte）小于消息头部长度，跳出小循环" % len(self.DataBuffer))
                            break

                        # 读取包头
                        # struct中:!代表Network order，3I代表3个unsigned int数据
                        headPack = struct.unpack('!3I', self.DataBuffer[:self.HeaderSize])
                        bodySize = headPack[1]

                        # 分包情况处理，跳出函数继续接收数据
                        if len(self.DataBuffer) < self.HeaderSize+bodySize :
                            print("LOG________数据包（%s Byte）不完整（总共%s Byte），跳出小循环" % (len(self.DataBuffer), self.HeaderSize+bodySize))
                            break
                        # 读取消息正文的内容
                        body = self.DataBuffer[self.HeaderSize:self.HeaderSize+bodySize]

                        # 数据处理
                        self.dataHandle(headPack, body)

                        # 粘包情况的处理
                        self.DataBuffer = self.DataBuffer[self.HeaderSize+bodySize:] # 获取下一个数据包，类似于把数据pop出

        except ConnectionResetError as x:
            print(x.strerror)
            g_conn_pool.remove(self.request)
            
 
 
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == '__main__':
    print('服务程序开启')
    server=socketserver.ThreadingTCPServer(((HOST, PORT)),ZxServer)

    # 新开一个线程运行服务端
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()


    print('XX')
 

    # 主线程逻辑
    while True:
        cmd = input("""--------------------------
输入1:查看当前在线人数
输入2:给指定客户端发送消息
输入3:关闭服务端
""")
        if cmd == '1':
            print("--------------------------")
            print("当前在线人数：", len(g_conn_pool))
        elif cmd == '2':
            print("--------------------------")
            index, msg = input("请输入“索引,消息”的形式：").split(",")
            g_conn_pool[int(index)].sendall(msg.encode(encoding='utf8'))
        elif cmd == '3':
            server.shutdown()
            server.server_close()
            exit()

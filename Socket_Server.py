import socket
import struct


#主机地址
HOST='127.0.0.1'
#主机端口
PORT=7654
#缓冲区
DataBuffer=bytes()
#头部长度
HeaderSize=12
#数据包计数器
sn=0

def dataHandle(headPack, body):
    global sn
    sn +=1
    print ("第%s个数据包" %sn)
    print("版本号:%s, 内容长度:%s, 命令:%s" % headPack)
    print(body.decode())
    print("")

if __name__ == '__main__':
    print ("程序开始")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if data:
                    # 把数据存入缓冲区，类似于push数据
                    DataBuffer += data
                    while True:
                        if len(DataBuffer) < HeaderSize:
                            print("数据包（%s Byte）小于消息头部长度，跳出小循环" % len(DataBuffer))
                            break

                        # 读取包头
                        # struct中:!代表Network order，3I代表3个unsigned int数据
                        headPack = struct.unpack('!3I', DataBuffer[:HeaderSize])
                        bodySize = headPack[1]

                        # 分包情况处理，跳出函数继续接收数据
                        if len(DataBuffer) < HeaderSize+bodySize :
                            print("数据包（%s Byte）不完整（总共%s Byte），跳出小循环" % (len(DataBuffer), HeaderSize+bodySize))
                            break
                        # 读取消息正文的内容
                        body = DataBuffer[HeaderSize:HeaderSize+bodySize]

                        # 数据处理
                        dataHandle(headPack, body)

                        # 粘包情况的处理
                        DataBuffer = DataBuffer[HeaderSize+bodySize:] # 获取下一个数据包，类似于把数据pop出
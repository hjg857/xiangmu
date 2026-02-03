import socket
try:
    print(socket.getaddrinfo('smtp.qq.com', 465))
    print("DNS解析成功！")
except Exception as e:
    print(f"DNS解析失败: {e}")
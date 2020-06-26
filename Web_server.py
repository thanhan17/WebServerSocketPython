import os
import socket
import threading
HOST = '0.0.0.0'
PORT = 80
sr = 'ServerRoot'
accessInfo = False
def parse_header(data):
    h_lines = data.split('\r\n')
    h_words = h_lines[0].split(' ')
    d_words = {}
    l = [h_lines.index(i) for i in h_lines if 'Cookie' in i]
    if (len(l) != 0):
        cookie_value = h_lines[l[0]].split(' ')[1].split('=')[1]
        d_words['Cookie'] = cookie_value
    else:
        d_words['Cookie'] = "DELETED"
    l = [h_lines.index(i) for i in h_lines if 'Content-Length' in i]
    if (len(l) != 0):
        c_length = h_lines[l[0]].split(' ')[1]
        d_words['Content-Length'] = c_length
    else:
        d_words['Content-Length'] = "0"
    d_words['Method'] = h_words[0]
    d_words['Path'] = h_words[1]
    d_words['Version'] = h_words[2][5:8]
    h_lines_len = len(h_lines)
    d_words['Data'] = h_lines[h_lines_len-1]
    if(d_words['Data'].split('&')[0].split('=')[0] == "_method"):
        d_words['Method'] = d_words['Data'].split('&')[0].split('=')[1]
    return d_words
      
def reDirect(url, conn):
    response_header = 'HTTP/1.1 301 Moved Permanently\nLocation: '+ url + '\nConnection: Keep-Alive\nContent-length: 0\n\n'
    conn.sendall(response_header.encode('utf-8'))
    conn.close()

def openSR(url, conn): #Send file on ServerRoot folder
    response = ("HTTP/1.1 200 OK\r\n\r\n").encode('utf-8')
    f = open(sr + url,"rb")
    response_body = f.read()         
    f.close()
    response += response_body
    conn.sendall(response)
    conn.close()
    
def ConnHandler(conn, addr):
    data = conn.recv(1024).decode('utf-8')
    print("Recieved Request:\n")
    print(data)
    if not data:
        conn.close()
        return
    parsed_fields = {}
    parsed_fields = parse_header(data)
    print(parsed_fields)
    req_file = ''
    global accessInfo
    if parsed_fields['Method'] == 'POST':
        if parsed_fields['Path'] == '/info.html' and parsed_fields['Data'] == 'uname=admin&psw=admin':
            accessInfo = True
            reDirect('/info.html', conn)
            return
    if parsed_fields['Method'] == 'GET':
        if len(parsed_fields['Path'])==1:
            reDirect('/index.html', conn)
            return
        if parsed_fields['Path'] == '/info.html':
            if accessInfo:
                openSR('/info.html', conn)
            else:
                reDirect('/404.html', conn)
            return
         if parsed_fields['Path'] == '/files.html':
             pass
        req_file = sr + parsed_fields['Path']
    if (os.path.isfile(req_file)):
        response_header = ("HTTP/1.1 200 OK\r\n\r\n")
    else:
        reDirect('/404.html',conn)
        return
    file_content = open(req_file,"rb")
    response_body = file_content.read()
    sock = response_header.encode('utf-8')
    sock += response_body
    conn.sendall(sock)
    file_content.close()
    conn.close()
#main
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print('Error while creating socket')
    sys.exit()
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
try:
    s.bind((HOST,PORT))
except socket.error:
    print("Error while binding host")
    sys.exit()
print("Socket bind successful")
print('Serving on http://'+HOST+':'+str(PORT))
s.listen(3)
print("Socket is now listening, ready for connections")
while True:
   conn,addr = s.accept()
   print("Connected to: " + str(addr[0]) + ":" + str(addr[1]) + "\n")
   ConnThread = threading.Thread(target=ConnHandler, args=(conn, addr))
   ConnThread.start()
conn.close()
s.close()

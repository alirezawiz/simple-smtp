import socket
from socket import *
import sys
from os import path
import re
from com.gmail.micheal.utils import *
from _thread import *
from datetime import datetime

serverName = '127.0.0.1'
serverPort = 5437
threadCount = 0


def start_smtp(connectionSocket, cName):
    ok_handshaking = False
    mailToInboxPath = ''
    try:
        # Hand Shaking
        helo = connectionSocket.recv(1024).decode('utf_8')
        print("Handshaking: " + helo)
        if helo[:4] == 'HELO' and helo[5:] == cName[0]:
            ok_handshaking = True
            helo_ack = 'S: 250 Hello ' + helo[5:] + '. Pleased to meet you.'
            connectionSocket.send(helo_ack.encode('utf_8'))
    except:
        print_err('HELO error. Try again.')
        sys.exit()

    while ok_handshaking:
        message = ""
        mailFrom = connectionSocket.recv(1024).decode('utf_8')
        if re.match(r'^RCPT TO:', mailFrom) or re.match(r'^DATA', mailFrom):
            connectionSocket.send('S: 503 Bad sequence of commands.'.encode('utf_8'))
            continue
        elif not bool(re.match(r'MAIL(\s+)FROM(\s*):(\s*)<(\s*\w+\.*\w*)+@(gmail|yahoo)(\.)com(\s*)>', mailFrom)):
            connectionSocket.send('S: 501 Syntax error in parameters or arguments.'.encode('utf_8'))
            continue
        else:
            if check_valid_from_mail(cName, str(mailFrom)):
                print(mailFrom)
                message += "<email_from> " + re.findall(r'[\w\.-]+@[\w]+[\.]com', mailFrom)[0] + " </email_from>\n"
                connectionSocket.send('S: 250 OK.'.encode('utf_8'))
            else:
                connectionSocket.send('S: 521 Server does not accept mail'.encode('utf_8'))
                continue

        is_rcpt_received = False
        while ok_handshaking:
            # receive receipt
            receipt = connectionSocket.recv(1024).decode('utf_8')
            # checks for out of order commands
            if is_rcpt_received and re.match(r'^DATA', receipt):
                break
            if re.match(r'RCPT(\s+)TO(\s*):(\s*)<(\s*\w+\.*\w*)+@(gmail|yahoo)(\.)com(\s*)>', receipt):
                if not check_rcpt_exist(receipt):
                    rcpt_msg = 'S: 550 Requested action not taken: mailbox unavailable.'
                else:
                    is_rcpt_received = True
                    message += "<email_to> " + re.findall(r'[\w\.-]+@[\w]+[\.]com', receipt)[0] + " </email_to>\n"
                    mailToInboxPath = get_rcpt_inbox_path(receipt)
                    print(receipt)
                    rcpt_msg = 'S: 250 OK.'
                connectionSocket.send(rcpt_msg.encode('utf_8'))
                continue
            else:
                connectionSocket.send('S: 501 Syntax error in parameters or arguments.'.encode('utf_8'))
                continue

        is_data_sent = False
        while ok_handshaking and not is_data_sent:
            if not re.match(r'^DATA', receipt):
                connectionSocket.send('S: 500 Syntax error: command unrecognized'.encode('utf_8'))
                continue
            else:
                connectionSocket.send('S: 354 Start mail input; end with '
                                      '<CRLF>.<CRLF>'.encode('utf_8'))

            buffer_data = ""
            while ok_handshaking:
                # receive msg until QUIT
                data = connectionSocket.recv(1024).decode('utf_8')
                buffer_data += data + "\n"
                print(data)
                if data == '.':
                    message += "<email_data>\n" + buffer_data + "</email_data>\n"
                    connectionSocket.send('S: 250 Message accepted for delivery.'.encode('utf_8'))
                    sendCmd = connectionSocket.recv(1024).decode('utf_8')
                    print(sendCmd)
                    if re.match(r'SEND', sendCmd):
                        is_data_sent = True
                        fileName = mailToInboxPath + "/" + str(datetime.now().time())
                        with open(f'{fileName}.txt', 'a') as myfile:
                            myfile.write(message)
                        connectionSocket.send('S: 250 Email sent.'.encode('utf_8'))
                        break
                    else:
                        connectionSocket.send('S: 503 Bad sequence of commands.'.encode('utf_8'))
                        continue
                else:
                    connectionSocket.send(data.encode('utf_8'))
                    continue

        quitMsg = connectionSocket.recv(1024).decode('utf_8')
        print(quitMsg)
        if re.match(r'QUIT', quitMsg):
            connectionSocket.send('S: 221 Server closing transition channel.'.encode('utf_8'))
        else:
            connectionSocket.send('Error happend when server closing.'.encode('utf_8'))
        ok_handshaking = False


def get_rcpt_inbox_path(receipt):
    receipt = re.findall(r'[\w\.-]+@[\w]+[\.]com', receipt)[0].replace('@', '.').split('.')
    return receipt[2] + "/" + receipt[1] + "/" + receipt[0] + "/inbox"


def check_rcpt_exist(receipt):
    receipt = re.findall(r'[\w\.-]+@[\w]+[\.]com', receipt)[0].replace('@', '.').split('.')
    if path.exists(receipt[2] + "/" + receipt[1] + "/" + receipt[0]):
        return True
    else:
        return False


def check_valid_from_mail(cName, mailFrom):
    mailFrom = re.findall(r'[\w\.-]+@[\w]+[\.]com', mailFrom)[0]
    ch = cName[0] + '@' + cName[1] + '.' + cName[2]
    return ch == mailFrom


def accept_connections(serverSocket):
    try:
        # Connection accepted
        client, addr = serverSocket.accept()
        client.send('S: 220 "127.0.0.1" ESMTP Postfix'.encode('utf_8'))
        print("Connection accepted: " + str(addr))
        clientOK = client.recv(1024).decode('utf_8')
        print(clientOK)
        cName = clientOK.split('.')
        client.send('S: 250 OK.'.encode('utf_8'))
        start_new_thread(start_smtp, (client, cName))
    except:
        print_err('Socket connection error.')
        sys.exit()


def start_server(host, port):
    serverSocket = socket(AF_INET, SOCK_STREAM)
    try:
        serverSocket.bind((host, port))
    except socket.error as e:
        print_err(str(e))
    print('Server Running...')
    serverSocket.listen()
    while True:
        accept_connections(serverSocket)


if __name__ == '__main__':
    start_server(serverName, serverPort)

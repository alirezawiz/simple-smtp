from socket import *
import sys
import re
from utils import *

mailServer = '127.0.0.1'
mailServerPort = 5437
clientHost = 'micheal.gmail.com'


def start_smtp(clientSocket):
    # Send HELO Command and print server respond
    heloCommand = input('\033[1;37m' + 'C: ')
    clientSocket.send(heloCommand.encode('utf_8'))
    recv1 = clientSocket.recv(1024).decode('utf_8')
    print_server(recv1)
    if recv1[3:6] != '250':
        print_err('Unable to connect to server. Please try again later.')
        clientSocket.close()
        sys.exit()

    # Send MAIL FROM command and print server response.
    while True:
        # input sender mail
        while True:
            mailfrom = input('\033[1;37m' + 'C: ')
            clientSocket.send(mailfrom.encode('utf_8'))
            recv2 = clientSocket.recv(1024).decode('utf_8')
            print_server(recv2)
            if recv2[3:6] != '250':
                print_err('Please enter a valid command Mail From.')
                continue
            else:
                break

        isRCPT = False
        # input email recipients separated by comma and space
        while True:
            command = input('\033[1;37m' + 'C: ')
            if isRCPT and re.match(r'^DATA', command):
                break
            clientSocket.send(command.encode('utf_8'))
            okTo = clientSocket.recv(1024).decode('utf_8')
            print_server(okTo)
            if okTo[3:6] != '250':
                print_err('Email address is invalid. please re-enter')
                continue
            else:
                isRCPT = True

        # Send DATA command to server
        clientSocket.send(command.encode('utf_8'))
        okData = clientSocket.recv(1024).decode('utf_8')
        print_server(okData)
        if okData[3:6] != '354':
            print_err('There is an error.')

        while True:
            readData = input('\033[1;37m' + 'C: ')
            if readData == '':
                readData = '\r'
            clientSocket.sendall(readData.encode('utf_8'))
            okEnd = clientSocket.recv(1024).decode('utf_8')
            if okEnd[3:6] == '250':
                print_server(okEnd)
                sendCmd = input('\033[1;37m' + 'C: ')
                clientSocket.send(sendCmd.encode('utf_8'))
                sendMsg = clientSocket.recv(1024).decode('utf_8')
                print_server(sendMsg)
                if sendMsg[3:6] != '250':
                    print_err('Can not send data to server. please re-enter data.')
                    continue
                else:
                    break
            else:
                continue

        quitCmd = input('\033[1;37m' + 'C: ')
        clientSocket.send(quitCmd.encode('utf_8'))
        quitMsg = clientSocket.recv(1024).decode('utf_8')
        if quitMsg[3:6] != '221':
            print_err('There was an error. Quitting.')
            break
        else:
            print_server(quitMsg)
            break


def start_client():
    # Create socket called clientSocket and establish a TCP connection with mailserver
    clientSocket = socket(AF_INET, SOCK_STREAM)

    # Port number may be change according to the mail server
    clientSocket.connect((mailServer, mailServerPort))
    recv = clientSocket.recv(1024).decode('utf_8')
    print_server(recv)
    if recv[3:6] != '220':
        print_err('Unable to connect to server. Please try again later.')
        clientSocket.close()
        sys.exit()

    clientSocket.send(clientHost.encode('utf_8'))
    clientOK = clientSocket.recv(1024).decode('utf_8')
    if clientOK[3:6] != '250':
        print_err('Unable to connect to server. Please try again later.')
        clientSocket.close()
        sys.exit()

    while True:
        print('\033[0;32m' + 'Menu: SMTP() - EXIT()')
        option = input('\033[1;32m' + '>>> ')
        if option == 'SMTP()':
            start_smtp(clientSocket)
        elif option == 'EXIT()':
            break
        else:
            print_err(">>> Please Enter Correct Option - try again")
    clientSocket.close()
    sys.exit()


if __name__ == '__main__':
    start_client()

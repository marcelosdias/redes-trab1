from socket import *
import os
import ctypes

HOST = ''
PORT = 3333
ADDRESS = (HOST, PORT)
BUF_SIZE = 1024
PATH = './uploads'

client = socket(AF_INET, SOCK_STREAM)
client.connect(ADDRESS)
print('connected to', ADDRESS)

command = 'POST#NAME:au_marvel_theavengers_ageofultron_movie_poster_5705ee77.jpeg;MULT:COLOR=1.2-CONTRAST=1.2-SPLIT=red,green'
#command = 'POST#NAME:unknown.png;SINGLE:GRAYSCALE'

# command = 'GET#NAME:unknown-edited-2.png'

header = command.split('#')[0]

file_name = (command.split(";")[0]).split(":")[1]

command_size = ctypes.c_uint32(len(command))

client.send(bytes(command_size))
client.send(command.encode('utf-8'))

message_size = client.recv(4)
message_size_int = int.from_bytes(message_size, byteorder='little')
message = (client.recv(message_size_int).decode('utf-8')).lower()

print(message)

if not ("400" in message):
    if header.lower() == 'post':
        full_path = os.path.join(PATH, file_name)

        file_size = ctypes.c_uint32(os.stat(full_path).st_size)

        client.send(bytes(file_size))

        with open(full_path, 'rb') as file:
            file_content = file.read(BUF_SIZE)

            while file_content:
                client.send(file_content)
                file_content = file.read(BUF_SIZE)

    message_size = client.recv(4)
    message_size_int = int.from_bytes(message_size, byteorder='little')
    message = (client.recv(message_size_int).decode('utf-8')).lower()

    print(message)

    if not ("400" in message):
        rcv_file_name_size = client.recv(4)
        file_name_size = int.from_bytes(rcv_file_name_size, byteorder='little')
        rcv_file_name = client.recv(file_name_size).decode('utf-8')
        rcv_file_size = client.recv(4)
        file_size = int.from_bytes(rcv_file_size, byteorder='little')

        new_full_path = full_path = os.path.join(PATH, rcv_file_name)

        with open(new_full_path, 'wb') as file:
            while file_size > 0:
                file_content = client.recv(min(BUF_SIZE, file_size))
                file.write(file_content)
                file_size -= len(file_content)

        message_size = client.recv(4)
        message_size_int = int.from_bytes(message_size, byteorder='little')
        message = (client.recv(message_size_int)).decode('utf-8')

        print(message)

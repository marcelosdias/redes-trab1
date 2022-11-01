from socket import *
import os
import ctypes

from PIL import Image, ImageEnhance, ImageFilter

count = 0

path = './downloads/'
BUF_SIZE = 1024

new_files = []

header_options = ['get', 'post']
body_options = ['name', 'mult', 'single']

def create_connection():
    HOST = ''
    PORT = 3333
    ADDRESS = (HOST, PORT)
    new_socket = socket(AF_INET, SOCK_STREAM)
    new_socket.bind(ADDRESS)
    new_socket.listen(5)

    return new_socket

def listen_requests(server_socket):
    print('listen for connection...')
    client_socket, addr = server_socket.accept()
    print('got connection from', addr)
    print('-------------------------')

    return client_socket

def get_client_commands(client_socket):
    error = False

    command_size = client_socket.recv(4)
    command_size_int = int.from_bytes(command_size, byteorder='little')
    command = (client_socket.recv(command_size_int).decode('utf-8')).lower()

    if not (is_correct_message(command)):
        send_message(client_socket, 'Bad Request', '400')
        error = True

    header, body = command.split('#')

    list_comands = body.split(';')

    send_message(client_socket, 'Message Received', '200')

    return header, list_comands, error

def is_correct_message(command):
    header, body = command.split('#')

    if not(header in header_options):   
        return False

    if header == 'post':
        if len(body.split(';')) != 2:
            return False

        first_body_option = (body.split(';')[0]).split(':')[0]
        second_body_option = (body.split(';')[1]).split(':')[0]

        if first_body_option == 'name' and (second_body_option == 'mult' or second_body_option == 'single'):
            return True
    else:
        first_body_option = (body.split(';')[0]).split(':')[0]

        if len(body.split(';')) != 1:
            return False

        if first_body_option == 'name':
            return True
    return False

def send_message(client_socket, message, code):
    error_message = (str(f"Code {code}: {message}")).encode('utf-8')

    error_message_size = ctypes.c_uint32(len(error_message))

    client_socket.send(bytes(error_message_size))
    client_socket.send(error_message)
        
def load_image(client_socket, file_name):
    received_file_size = client_socket.recv(4)
    file_size = int.from_bytes(received_file_size, byteorder='little')

    full_path = os.path.join(path, file_name)

    new_files.append(full_path)
    with open(full_path, 'wb') as file:
        while file_size > 0:
            file_content = client_socket.recv(min(BUF_SIZE, file_size))
            file.write(file_content)
            file_size -= len(file_content)
            
def edit_image(file_name, command):
    global count
    new_image = ''

    full_path = path + file_name

    formatted_name, format = file_name.split('.')

    if not('-edited' in file_name):
        new_file_name = '{}-edited-{}.{}'.format(formatted_name, count,format)
        new_full_path = './downloads/{}'.format(new_file_name)
    else:
        new_file_name = '{}.{}'.format(formatted_name, format)
        new_full_path = './downloads/{}'.format(new_file_name)
    if command == 'grayscale':
        image = Image.open(full_path)

        color = ImageEnhance.Color(image)

        new_image = color.enhance(0)

        new_image.save(new_full_path)
    elif "resize" in command: 
        width, height = (command.split("=")[1]).split(",")

        image = Image.open(full_path)

        new_image = image.resize((int(width), int(height)))

        new_image.save(new_full_path)

    elif "contrast" in command:
        contrast_value = float(command.split("=")[1]) #talvez isso não esteja certo

        image = Image.open(full_path)

        contrast = ImageEnhance.Contrast(image)
        new_image = contrast.enhance(contrast_value)

        new_image.save(new_full_path)

    elif "color" in command:
        color_value = float(command.split("=")[1])

        image = Image.open(full_path)

        color = ImageEnhance.Color(image)

        new_image = color.enhance(color_value)

        new_image.save(new_full_path)

    elif "brightness" in command:
        brightness_value = float(command.split("=")[1])

        image = Image.open(full_path)

        brightness = ImageEnhance.Brightness(image)

        new_image = brightness.enhance(brightness_value)

        new_image.save(new_full_path)

    elif "sharpness" in command:
        sharpness_value = float(command.split("=")[1])

        image = Image.open(full_path)

        sharpness = ImageEnhance.Sharpness(image)

        new_image = sharpness.enhance(sharpness_value)

        new_image.save(new_full_path)

    elif "cropping" in command:
        left, top, right, lower = command.split("=")[1].split(",")

        image = Image.open(full_path)

        box = (int(left), int(top), int(right), int(lower))

        new_image = image.crop(box)

        new_image.save(new_full_path)

    elif "rotate" in command:
        rotation_value = float(command.split("=")[1])

        image = Image.open(full_path)

        new_image = image.rotate(rotation_value, expand=True)

        new_image.save(new_full_path)

    elif "flip" in command:
        if "left_right" in command:
            image = Image.open(full_path)

            new_image = image.transpose(Image.FLIP_LEFT_RIGHT)

            new_image.save(new_full_path)

        elif "top_bottom" in command:
            image = Image.open(full_path)

            new_image = image.transpose(Image.FLIP_TOP_BOTTOM)

            new_image.save(new_full_path)

    elif "split" in command:   
        image = Image.open(full_path)

        im1 = Image.Image.split(image)

        if "red,green" in command:
            new_image = Image.merge("RGB", (im1[1], im1[0], im1[2]))
        elif "green,blue" in command: 
            new_image = Image.merge("RGB", (im1[0], im1[2], im1[1]))
        elif "red,blue" in command:
            new_image = Image.merge("RGB", (im1[2], im1[2], im1[0]))

        new_image.save(new_full_path)
    
    elif "gauss" in command:
        image = Image.open(full_path)

        new_image = image.filter(ImageFilter.GaussianBlur)

        new_image.save(new_full_path)

    new_files.append(new_full_path)

    return new_file_name, new_full_path

def send_image(new_file_name, new_full_path):
    filename_bytes = new_file_name.encode('utf-8')
    filename_size = ctypes.c_uint32(len(filename_bytes))
    file_size = ctypes.c_uint32(os.stat(new_full_path).st_size)

    client_socket.send(bytes(filename_size))
    client_socket.send(filename_bytes)
    client_socket.send(bytes(file_size))

    with open(new_full_path, 'rb') as file:
        file_content = file.read(BUF_SIZE)

        while file_content:
            client_socket.send(file_content)
            file_content = file.read(BUF_SIZE)
        
    return file_name


def is_valid_image(client_socket, file_name):
    images = os.listdir("./downloads")

    for img in images:
        if img == file_name:
            send_message(client_socket, 'Message Received', '200')
            return True
    
    send_message(client_socket, 'Bad Request', '400')

    return False

server_socket = create_connection()

while True:
    count_commands = 0
    client_socket = listen_requests(server_socket)

    header, body, error = get_client_commands(client_socket)

    if not error:
        file_name = body[0].split(':')[1]

        if header == 'post':
            list_commands = (body[1].split(':')[1]).split('-')

            load_image(client_socket, file_name)

            len_comands = len(list_commands)

            for command in list_commands:
                file_name, new_path = edit_image(file_name, command)
                count_commands += 1

            if count_commands == len_comands:
                send_message(client_socket, 'Image Received Successfully', '200')
                
                file_name = send_image(file_name, new_path)
                count += 1

                send_message(client_socket, 'Image Sent Successfully', '200')
                
        else:
            if is_valid_image(client_socket, file_name):
                file_name = send_image(file_name, f"./downloads/{file_name}")
                send_message(client_socket, 'Image Sent Successfully', '200')
       
    client_socket.shutdown(0)
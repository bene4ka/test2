from socket import *
import sys
import argparse
import logging
import names
from client_log_config import Log
from threading import Thread
import tkinter
from jim import *

logger = logging.getLogger('app.main')


def arguments():
    """
    Принимает аргументы командной строки [ip, p, v], где:
    ip - адрес сервера, обязателен к вводу.
    p - порт, к которому будет совершено подключение. По умолчанию равен 7777.
    v - уровень логгирования (0=NOTSET, 1=DEBUG, 2=INFO 3=WARNING 4=ERROR 5=CRITICAL), по-умолчанию 2.
    :return: лист, где первым элементом является порт, а вторым - IP для подключения.
    """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-ip', default='127.0.0.1', metavar='<ip>', help='Server IP address', type=str)
    parser.add_argument('-p', default='7777', help='port of remote server', type=int)
    parser.add_argument('-v', default=1, help='verbose level', type=int)
    parsed_opts = parser.parse_args()
    port = parsed_opts.p
    address = parsed_opts.ip
    if parsed_opts.v == 0:
        logger.setLevel(logging.NOTSET)
    elif parsed_opts.v == 1:
        logger.setLevel(logging.DEBUG)
    elif parsed_opts.v == 2:
        logger.setLevel(logging.INFO)
    elif parsed_opts.v == 3:
        logger.setLevel(logging.WARNING)
    elif parsed_opts.v == 4:
        logger.setLevel(logging.ERROR)
    elif parsed_opts.v >= 5:
        logger.setLevel(logging.CRITICAL)
    else:
        # Если уровень логгирования выбран неверно, выводим сообщение и глушим клиент.
        logger.setLevel(logging.CRITICAL)
        logger.critical("UNEXPLAINED COUNT IN VERBOSITY LEVEL!")
        print("UNEXPLAINED COUNT IN VERBOSITY LEVEL!")
        sys.exit()
    logger.info('Попытка коннекта будет осуществлена на адрес {} и порт {}'.format(address, str(port)))
    return [port, address]


@Log()
def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(1024).decode('utf8')
            msg_list.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break


@Log()
def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    print('started send')
    msg = my_msg.get()
    json_msg = MessageSent.message(msg=msg, user_key=random_name)
    my_msg.set("")  # Clears input field.
    client_socket.send(json_msg)
    if msg == "@quit":
        print('cause close')
        client_socket.close()
        top.quit()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("@quit")
    send()


@Log()
def sock_conn(args):
    """
    Connects client to server.
    :param args: arguments of command line
    :return:
    """
    sock = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
    sock.connect((args[1], args[0]))  # Соединиться с сервером
    print('Connect')
    return sock


top = tkinter.Tk()
top.title("Veseliy chat")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

# ----Now comes the sockets part----
cmd_args = arguments()
random_name = names.get_full_name()
client_socket = sock_conn(cmd_args)

presence = MessageSent.presence(user_key=random_name)
client_socket.send(presence)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.

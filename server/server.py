# Серверная часть

import sys
import argparse
import logging
import select
from socket import *
from server_log_config import Log
from jim import *

logger = logging.getLogger('app.main')


@Log()
def arguments():
    """
    Принимает аргументы командной строки [p, n, v], где:
    p - порт, по которому будет работать серверный процесс. По умолчанию равен 7777.
    a - адрес интерфейса, на который будет совершен бинд. По умолчанию пуст, что означает бинд на все интерфейсы.
    v - уровень логгирования (0=NOTSET, 1=DEBUG, 2=INFO 3=WARNING 4=ERROR 5=CRITICAL), по-умолчанию 2.
    :return: лист, где первым элементом является порт, а вторым - IP для прослушки.
    """
    # Инициализация парсера.
    parser = argparse.ArgumentParser(description='Collect options.')
    # Описание доступных опций запуска.
    parser.add_argument('-p', default='7777', help='port', type=int)
    parser.add_argument('-a', default='', help='address', type=str)
    parser.add_argument('-v', default=2, help='verbose level', type=int)
    # Получаем список спарсеных опций.
    parsed_opts = parser.parse_args()
    # Получаем порт и адрес
    port = parsed_opts.p
    address = parsed_opts.a
    # Проверяем уровень логгирования.
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
        # Если уровень логгирования выбран неверно, выводим сообщение и глушим сервер.
        logger.setLevel(logging.CRITICAL)
        logger.critical("UNEXPLAINED COUNT IN VERBOSITY LEVEL!")
        print("UNEXPLAINED COUNT IN VERBOSITY LEVEL!")
        sys.exit()
    logger.info('Будем пробовать запуститься с портом {}'.format(str(port)) +
                (' на всех интерфейсах.' if address == '' else 'на интерфейсе {}.'.format(address)))
    # Возврат листа [порт, адрес]
    return [port, address]


@Log()
def sock_bind(args):
    """"
    Создает TCP-сокет и присваает порт и интерфейс, полученный из функции arguments()
    :param args: лист из порта в integer и адреса интерфейса в string.
    """
    s = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP.
    logger.info('Открыт сокет.')
    try:
        s.bind((args[1], args[0]))  # Присваивает порт 8888.
        logger.info('Удачно забиндились на порт и интерфейс.')
    except OSError:
        logger.error('Выбранный порт уже занят.')
    s.listen(5)  # Переходит в режим ожидания запросов, одновременно не болеее 5 запросов.
    s.settimeout(0.2)  # Set timeout
    logger.info('Перешли в режим LISTEN.')
    return s


@Log()
def read_requests(r_clients, all_clients):
    """
    Read requests from clients.
    :param r_clients: clients from which server can get message.
    :param all_clients: all currently connected clients.
    :return:
    """
    responses = {}  # Словарь ответов сервера вида {сокет: запрос}

    for sock in r_clients:
        try:
            data_json = sock.recv(1024)
            data = MessageRecv.respond(data_json)
            responses[sock] = data
        except:
            logging.info('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
            all_clients.remove(sock)

    return responses


@Log()
def write_responses(requests, w_clients, all_clients):
    """
    Broadcasts message which was received from any of clients to all connected clients.
    :param requests: contains dictionary with message from sending client.
    :param w_clients: clients which can receive message.
    :param all_clients: all currently connected clients.
    :return:
    """
    print('All clients: ' + str(all_clients))
    for sock in w_clients:  # For every client who able to receive messages
        if sock in requests:  # If there is a some message to send
            try:
                # Prepare and send answer for ALL.
                resp = requests[sock].encode('utf-8')
                for client in all_clients:
                    client.sendall(resp)
            except:  # Socket unavailable, client disconneted.
                logging.info('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                sock.close()
                all_clients.remove(sock)


# main-функция
def main():
    args = arguments()
    s = sock_bind(args)
    clients = []
    usernames = []
    # Infinity cycle
    while True:
        try:
            conn, addr = s.accept()  # Gets connections
        except OSError as e:
            pass
        else:
            logger.info("Get connection request from {}".format(str(addr)))
            clients.append(conn)
        finally:
            # Check input/output event.
            wait = 10
            r = []
            w = []
            try:
                r, w, e = select.select(clients, clients, [], wait)
            except:
                pass  # Do nothing if someone disconnected.

            requests = read_requests(r, clients)  # Save clients requests.
            if requests:
                write_responses(requests, w, clients)  # Send message for all.


# Точка входа
if __name__ == '__main__':
    main()

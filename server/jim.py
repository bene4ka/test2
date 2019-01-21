import json
import time
import re

class Message:
    """
    Base Message class
    """

    @classmethod
    def pack(cls, dict_msg):
        """
        Создание сообщения, пригодного для отправки через TCP
        :param dict_msg: dict
        :return: str
        """
        str_msg = json.dumps(dict_msg)
        return str_msg.encode('utf8')

    @classmethod
    def unpack(cls, bt_str):
        """
        Распаквка полученного сообщения
        :param bt_str: str
        :return: dict
        """
        str_decoded = bt_str.decode('utf-8')
        return json.loads(str_decoded)


class MessageSent(Message):
    """
    Send message class
    """

    @classmethod
    def presence(cls, user_key='Guest', status_key='Online'):
        msg = {
            'action': 'presence',
            'time': int(time.time()),
            'user': {
                'user_name': user_key,
                'status': status_key
            }
        }
        return cls.pack(msg)

    @classmethod
    def message(cls, user_key='Guest', status_key='Online', msg=''):
        if_dest = re.findall(r'\@(\w+\ \w+)', msg)
        if len(if_dest) == 0:
            dest = 'All'
        else:
            dest = if_dest[0]
        msg = {
            'action': 'message',
            'time': int(time.time()),
            'message': msg,
            'to': dest,
            'user': {
                'user_name': user_key,
                'status': status_key
            }
        }
        return cls.pack(msg)


class MessageRecv(Message):
    """
    Receive message class
    """

    @classmethod
    def respond(cls, bt_str):
        data = cls.unpack(bt_str)
        if data.get('action') == 'presence':
            user_key = data.get('user').get('user_name')
            resp = user_key + ' joins to conversation!'
        elif data.get('action') == 'message':
            user_key = data.get('user').get('user_name')
            msg = data.get('message')
            resp = user_key + ': ' + msg
        else:
            resp = 'Error action, pal.'
        return resp

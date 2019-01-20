import json
import time

MESSAGE_SIZE = 1024


class Message:
    def __init__(self, **kwargs):
        self.__raw = kwargs
        self.__raw['time'] = int(time.time())

    def __bytes__(self):
        return '{}'.format(json.dumps(self.__raw)).encode('utf-8')

    def __str__(self):
        j_mesg = {
            'action': self.__raw['action']
        }
        return str(j_mesg)

    @property
    def action(self):
        return self.__raw['action'] if 'action' in self.__raw else None

    @property
    def type(self):
        return self.__raw['type'] if 'type' in self.__raw else None

    @property
    def message(self):
        return self.__raw['message'] if 'message' in self.__raw else None

    @property
    def user_name(self):
        try:
            name = self.__raw['user']['user_name']
        except ValueError:
            return None
        return name

    @property
    def status(self):
        try:
            name = self.__raw['user']['status']
        except ValueError:
            return None
        return name

    @property
    def destination(self):
        return self.__raw['to'] if 'to' in self.__raw else None

    @property
    def sender(self):
        return self.__raw['from'] if 'from' in self.__raw else None


def success(response=200, **kwargs):
    return Message(response=response, **kwargs)


def error(text, **kwargs):
    return Message(response=400, error=text, **kwargs)


def error_request(text, **kwargs):
    return Message(action='error', msg=text, **kwargs)

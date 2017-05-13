from sys import argv
from traceback import print_exc

from requests import request
from websocket import WebSocketApp


def trace(function):
    def wrap(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception:
            print_exc()
            exit()
    return wrap


class WebSockets():

    URL = 'wss://premws-pt2.365lpodds.com/zap/'

    DELIMITERS_MESSAGE = '\x00'
    DELIMITERS_RECORD = '\x01'
    DELIMITERS_FIELD = '\x02'

    TYPES_CLIENT_ID = '4'
    TYPES_TOPIC_LOAD_MESSAGE = '\x14'
    TYPES_DELTA_MESSAGE = '\x15'
    TYPES_SUBSCRIBE = '\x16'
    TYPES_PING_CLIENT = '\x19'

    @trace
    def __init__(self, id):
        self.id = id
        self.session_id = self.get_session_id()

    @trace
    def get_session_id(self):
        response = None
        try:
            response = request(method='GET', url='https://www.bet365.com/?#/AS/B1/')
        except Exception:
            pass
        if not response:
            return
        return response.cookies['pstk']

    @trace
    def open(self):
        self.connection = WebSocketApp(
            self.URL,
            on_open=self.on_open,
            on_close=self.on_close,
            on_data=self.on_data,
            on_message=self.on_message,
            on_error=self.on_error,
            header={
                'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
                'Sec-WebSocket-Protocol': 'zap-protocol-v1',
                'Sec-WebSocket-Version': '13',
            },
        )
        self.connection.run_forever()

    @trace
    def on_open(self, _):
        print('Open')
        message = '#\x03P\x01__time,S_%s' % self.session_id
        print(repr(message))
        self.connection.send(bytearray(message, 'utf-8'))

    @trace
    def on_close(self, _):
        print('Close')

    @trace
    def on_data(self, a, b, c):
        a = bytearray(a, 'utf-8')
        print(repr(a))
        b = bytearray(b, 'utf-8')
        print(repr(b))
        c = bytearray(c, 'utf-8')
        print(repr(c))

    @trace
    def on_message(self, _, message):
        message = bytearray(message, 'utf-8')
        print(repr(message))

    @trace
    def on_error(self, _, error):
        print('Error', repr(error))


@trace
def main(options):
    web_sockets = WebSockets(options[1])
    web_sockets.open()


if __name__ == '__main__':
    main(argv)

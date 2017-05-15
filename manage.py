from sys import argv
from traceback import print_exc

from requests import request
from ws4py.client.threadedclient import WebSocketClient


def trace(function):
    def wrap(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception:
            print_exc()
            exit()
    return wrap


class WebSockets(WebSocketClient):

    URL = u'wss://premws-pt1.365lpodds.com/zap/'

    HEADERS = [
        (u'Sec-WebSocket-Extensions', u'permessage-deflate;client_max_window_bits'),
        (u'Sec-WebSocket-Protocol', u'zap-protocol-v1'),
        (u'Sec-WebSocket-Version', u'13'),
    ]

    DELIMITERS_MESSAGE = u'\x08'
    DELIMITERS_RECORD = u'\x01'
    DELIMITERS_FIELD = u'\x02'

    TYPES_TOPIC_LOAD_MESSAGE = u'\x14'
    TYPES_DELTA_MESSAGE = u'\x15'
    TYPES_SUBSCRIBE = u'\x16'
    TYPES_PING_CLIENT = u'\x19'

    TOPICS = [
        u'CONFIG_1_3',
        u'OVInPlay_1_3',
        u'Media_L1_Z3',
        u'XL_L1_Z3_C1_W5',
    ]

    @trace
    def __init__(self, id):
        self.id = id
        super(WebSockets, self).__init__(self.URL, headers=self.HEADERS)
        self.session_id = get_session_id()

    @trace
    def connect(self):
        if not self.session_id:
            print('Invalid Session ID')
            return
        super(WebSockets, self).connect()

    @trace
    def opened(self):
        print('Opened')
        message = u'#\x03P\x01__time,S_%s\x00' % self.session_id
        self.send(message)

    @trace
    def closed(self, code, reason=None):
        print('Closed', code, reason)

    @trace
    def received_message(self, message):
        message = unicode(message)
        print('<=', repr(message))
        message = self.decode(message)
        if message[0][0] == u'100':
            message = u'\x16\x00' + u','.join(self.TOPICS) + u'\x01\x00'
            self.send(message)
            return
        if message[0][0] == u'\x14EMPTY':
            message = u'\x16\x006V64507930C1A_1_3\x01\x00'
            self.send(message)
            message = u'\x16\x0015332427912M1_1_3\x01\x00'
            self.send(message)
            return

    @trace
    def send(self, message):
        print('=>', repr(message))
        message = bytearray(message, 'utf-8')
        super(WebSockets, self).send(message)

    @trace
    def decode(self, message):
        message = message.strip(self.DELIMITERS_MESSAGE)
        message = message.split(self.DELIMITERS_RECORD)
        message = [m.split(self.DELIMITERS_FIELD) for m in message]
        message = [[item for item in items if item] for items in message]
        message = [m for m in message if m]
        return message


@trace
def get_session_id():
    response = None
    try:
        response = request(method='GET', url='https://www.bet365.com/?#/AS/B1/')
    except Exception:
        pass
    if not response:
        return
    return response.cookies['pstk']


@trace
def main(options):
    try:
        web_sockets = WebSockets(options[1])
        web_sockets.connect()
        web_sockets.run_forever()
    except KeyboardInterrupt:
        web_sockets.close()


if __name__ == '__main__':
    main(argv)

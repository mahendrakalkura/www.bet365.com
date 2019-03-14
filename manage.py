from pprint import pprint

from requests import request
from ws4py.client.threadedclient import WebSocketClient


class WebSockets(WebSocketClient):

    _URLS_CONNECTION = u'wss://premws-pt1.365lpodds.com/zap/'
    _URLS_SESSION_ID = u'https://www.bet365.com.cy/en/?#/AS/B1/'

    _HEADERS = [
        (u'Sec-WebSocket-Extensions', u'permessage-deflate;client_max_window_bits'),
        (u'Sec-WebSocket-Protocol', u'zap-protocol-v1'),
        (u'Sec-WebSocket-Version', u'13'),
    ]

    _DELIMITERS_RECORD = u'\x01'
    _DELIMITERS_FIELD = u'\x02'
    _DELIMITERS_HANDSHAKE = u'\x03'
    _DELIMITERS_MESSAGE = u'\x08'

    _ENCODINGS_NONE = u'\x00'

    _TYPES_TOPIC_LOAD_MESSAGE = u'\x14'
    _TYPES_DELTA_MESSAGE = u'\x15'
    _TYPES_SUBSCRIBE = u'\x16'
    _TYPES_PING_CLIENT = u'\x19'
    _TYPES_TOPIC_STATUS_NOTIFICATION = u'\x23'

    _TOPICS = [
        '__host',
        'CONFIG_1_3',
        'LHInPlay_1_3',
        'Media_l1_Z3',
        'XI_1_3',
    ]

    _MESSAGES_SESSION_ID = u'%s%sP%s__time,S_%%s%s' % (
        _TYPES_TOPIC_STATUS_NOTIFICATION,
        _DELIMITERS_HANDSHAKE,
        _DELIMITERS_RECORD,
        _ENCODINGS_NONE,
    )

    _MESSAGES_SUBSCRIPTION = u'%s%s%%s%s' % (
        _TYPES_SUBSCRIBE,
        _ENCODINGS_NONE,
        _DELIMITERS_RECORD,
    )

    def __init__(self):
        super(WebSockets, self).__init__(self._URLS_CONNECTION, headers=self._HEADERS)

    def connect(self):
        print(u'opening connection...')
        super(WebSockets, self).connect()

    def disconnect(self):
        print(u'closing connection...')

    def opened(self):
        print(u'opened connection')
        session_id = self._fetch_session_id()
        if not session_id:
            self.disconnect()
            return
        message = self._MESSAGES_SESSION_ID % session_id
        self._send(message)

    def closed(self, code, reason=None):
        print(u'closed connection')
        print(u'code:', code)
        print(u'reason:', reason)

    def received_message(self, message):
        message = unicode(message)
        print(u'received message:', message)
        message = message.split(self._DELIMITERS_MESSAGE)
        while len(message):
            a = message.pop()
            b = a[0]
            if b == u'1':
                for topic in self._TOPICS:
                    m = self._MESSAGES_SUBSCRIPTION % topic
                    self._send(m)
                continue
            if b in [self._TYPES_TOPIC_LOAD_MESSAGE, self._TYPES_DELTA_MESSAGE]:
                matches = a.split(self._DELIMITERS_RECORD)
                path_config = matches[0].split(self._DELIMITERS_FIELD)
                pair = path_config.pop()
                read_it_message = pair[1:]
                l = a[(len(matches[0]) + 1):]
                pprint([read_it_message, l], width=1)
                continue

    def _send(self, message):
        print(u'sending message:', repr(message))
        self.send(message)

    def _fetch_session_id(self):
        print(u'fetching session id...')
        response = None
        try:
            response = request(method=u'GET', url=self._URLS_SESSION_ID)
        except Exception:
            pass
        if not response:
            print(u'session id: N/A')
            return
        session_id = response.cookies[u'pstk']
        print(u'session id:', session_id)
        return session_id


if __name__ == u'__main__':
    try:
        web_sockets = WebSockets()
        web_sockets.connect()
        web_sockets.run_forever()
    except KeyboardInterrupt:
        web_sockets.disconnect()

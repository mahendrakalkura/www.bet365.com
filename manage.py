from sys import argv
from traceback import print_exc

from websocket import WebSocketApp


def trace(function):
    def wrap(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception:
            print_exc()
            raise
    return wrap


class WebSockets():

    URL = 'wss://premws-pt2.365lpodds.com/zap/?uid=7187482066279285'

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
        pass

    @trace
    def open(self):
        self.connection = WebSocketApp(
            self.URL,
            on_open=self.on_open,
            on_close=self.on_close,
            on_message=self.on_message,
            on_error=self.on_error,
        )
        self.connection.run_forever()

    @trace
    def on_open(self, _):
        self.log('Open', None)

    @trace
    def on_close(self, _):
        self.log('Close', None)

    @trace
    def on_message(self, _, message):
        message = bytearray(message, 'utf-8')
        print(repr(message))

    @trace
    def on_error(self, _, error):
        self.log('Error', error)

    @trace
    def log(self, prefix, suffix):
        if prefix and suffix:
            prefix = prefix.ljust(28, ' ')
            suffix = repr(suffix)
            print('[+]', prefix, ':', suffix)
            return
        if prefix:
            print('[+]', prefix)
            return


@trace
def main(options):
    web_sockets = WebSockets(argv[1])
    web_sockets.open()


if __name__ == '__main__':
    main(argv)

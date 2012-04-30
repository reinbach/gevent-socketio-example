import json
import math
import time

from flask import Flask, render_template

import gevent
from gevent.pywsgi import WSGIServer
from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin

app = Flask(__name__)
app.debug = True

class SocketIOApp(object):
    """Stream sine values"""
    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith('/socket.io'):
            socketio_manage(environ, {'': SineWave});

class SineWave(BaseNamespace, BroadcastMixin):
    def on_sine(self, msg):
        while True:
            x = time.time()
            y = 2.5 * (1 + math.sin(x))
            self.broadcast_event('message', json.dumps(dict(x=x, y=y)))
            gevent.sleep(0.1)

@app.route("/")
def home():
    return render_template("index.html")

def main():
    # setup server to handle webserver requests
    http_server = WSGIServer(('', 8000), app)

    # setup server to handle websocket requests
    sio_server = SocketIOServer(
        ('', 9999), SocketIOApp(),
        namespace="socket.io",
        policy_server=False
    )

    gevent.joinall([
        gevent.spawn(http_server.serve_forever),
        gevent.spawn(sio_server.serve_forever)
    ])

if __name__ == "__main__":
    main()
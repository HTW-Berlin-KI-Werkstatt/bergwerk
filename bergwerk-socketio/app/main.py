import socketio
from sanic import Sanic
from sanic.response import html
from modules import handlers, utils
from time import sleep

HTML = """
Welcome to Bergwerk!
"""

BW_URL = "http://api:80"
SIO_PORT = 5005

# Create a Socket.IO server with enhanced logging

sio = socketio.AsyncServer(
    async_mode='sanic',
    cors_allowed_origins='*',
    path='/socket.io/',
    ping_timeout=1800,     # =30 minutes
    ping_interval=300      # = 5 minutes
)

# Sanic application for handling HTTP requests
app = Sanic(name='socketio_app')

sio.attach(app, socketio_path='/socket.io/')


@app.route('/')
async def index(request):
    return html(HTML)

@sio.event
async def connect(sid, environ):
    print(f'Connection established with SID: {sid}, Environment: {environ}')


@sio.event
async def disconnect(sid):
    print(f'Disconnected: SID {sid}')
    await handlers.handle_disconnect(sid)


@sio.on("session_request")
async def session_request(sid, data):
    await sio.emit("session_confirm", sid)
    print(f"User {sid} connected to socketIO endpoint.")


@sio.on("user_uttered")
async def user_uttered(sid, data):
    await handlers.handle_user_message(sid, data, sio, BW_URL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SIO_PORT)

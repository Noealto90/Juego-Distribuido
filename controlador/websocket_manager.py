import asyncio
import websockets
import json
from config.config import WS_HOST, WS_PORT

class WebSocketManager:
    def __init__(self):
        self.clients = set()
        self.game_states = {}
    
    async def register(self, websocket):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        finally:
            self.clients.remove(websocket)
    
    async def handle_message(self, websocket, message):
        try:
            data = json.loads(message)
            if data['type'] == 'score_update':
                await self.broadcast_score_update(data)
            elif data['type'] == 'game_state':
                await self.broadcast_game_state(data)
        except json.JSONDecodeError:
            print("Error al decodificar mensaje JSON")
    
    async def broadcast_score_update(self, data):
        if self.clients:
            message = json.dumps({
                'type': 'score_update',
                'game_id': data['game_id'],
                'score': data['score']
            })
            await asyncio.gather(
                *[client.send(message) for client in self.clients]
            )
    
    async def broadcast_game_state(self, data):
        if self.clients:
            message = json.dumps({
                'type': 'game_state',
                'game_id': data['game_id'],
                'state': data['state']
            })
            await asyncio.gather(
                *[client.send(message) for client in self.clients]
            )
    
    async def start_server(self):
        async with websockets.serve(self.register, WS_HOST, WS_PORT):
            await asyncio.Future()  # run forever 
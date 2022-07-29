import json
from channels.generic.websocket import WebsocketConsumer

class VideoConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()
        self.send(text_data=json.dumps({
            "type": "connection_established",
            'message': "You are connected"
        }))

    def receive(self, text_data):
        print(text_data)
        arr = []
        #nanaskdnas
        

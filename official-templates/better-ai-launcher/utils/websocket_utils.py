import json

active_websockets = set()

def send_websocket_message(message_type, data):
    message = json.dumps({'type': message_type, 'data': data})
    dead_sockets = set()
    for ws in active_websockets:
        try:
            ws.send(message)
        except Exception as e:
            print(f"Error sending WebSocket message: {str(e)}")
            dead_sockets.add(ws)
    
    # Remove dead sockets
    active_websockets.difference_update(dead_sockets)

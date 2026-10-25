import asyncio
import struct
import os
import base64
import websockets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SECRET_KEY = b'0123456789abcdef0123456789abcdef'
aesgcm = AESGCM(SECRET_KEY)

async def handle_connection(websocket):
    try:
        data = await websocket.recv()
        encrypted_data = base64.b64decode(data)
        
        nonce = encrypted_data[:12]
        packet_len = struct.unpack('>I', encrypted_data[12:16])[0]
        payload = encrypted_data[16:16+packet_len]
        
        decrypted = aesgcm.decrypt(nonce, payload, None)
        
        addr_len = struct.unpack('>H', decrypted[:2])[0]
        target_host = decrypted[2:2+addr_len].decode('utf-8')
        target_port = struct.unpack('>H', decrypted[2+addr_len:4+addr_len])[0]
        
        print(f"Подключаемся к: {target_host}:{target_port}")
        
        remote_reader, remote_writer = await asyncio.open_connection(target_host, target_port)
        
        async def pipe_ws_to_remote():
            try:
                while True:
                    data = await websocket.recv()
                    remote_writer.write(base64.b64decode(data))
                    await remote_writer.drain()
            except: pass

        async def pipe_remote_to_ws():
            try:
                while True:
                    data = await remote_reader.read(4096)
                    if not data: break
                    await websocket.send(base64.b64encode(data).decode('ascii'))
            except: pass
                
        await asyncio.gather(pipe_ws_to_remote(), pipe_remote_to_ws())
        
    except Exception as e:
        print(f"Ошибка сервера: {e}")
    finally:
        await websocket.close()

async def main():
    port = int(os.environ.get("PORT", 10000))
    async with websockets.serve(handle_connection, "0.0.0.0", port):
        print(f"Сервер запущен на порту {port}")
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())

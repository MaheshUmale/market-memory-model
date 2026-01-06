import asyncio
import websockets
import json

class DataIngestion:
    def __init__(self, uri):
        self.uri = uri
        self.connection = None

    async def connect(self):
        self.connection = await websockets.connect(self.uri)
        print(f"Connected to {self.uri}")

    async def listen(self):
        while True:
            try:
                message = await self.connection.recv()
                data = json.loads(message)
                if data.get("type") == "candle_update":
                    print(json.dumps(data, indent=2))
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

async def main():
    ingestion = DataIngestion("ws://localhost:8765")
    await ingestion.connect()
    await ingestion.listen()

if __name__ == "__main__":
    asyncio.run(main())

from server.server import Server
import asyncio

async def main():
    server = Server("./server/config.json")
    await server.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        server.dispose()
        
if __name__ == "__main__":
    asyncio.run(main())
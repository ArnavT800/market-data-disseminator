from client.client import MarketDataClient
import asyncio

async def main():
    client = MarketDataClient()
    client.connect('localhost:3000')

    client_task = asyncio.create_task(client.run())
    input_task = asyncio.create_task(user_input_loop(client))

    try:
        await asyncio.gather(client_task, input_task)
    except Exception as e:
        print(f"Error occurred with .gather: {e}")

    finally:
        await client.flush_queue()
        client_task.cancel()
        await client.channel.close()

async def user_input_loop(client):
    while True:
        print("Commands: ")
        print("S <instrument_id>: Subscribe to instrument with id")
        print("U <instrument_id>: Unsubscribe to instrument with id")
        input_thread_call = await asyncio.to_thread(input)
        user_inp = input_thread_call.strip().split(" ")
        if len(user_inp) != 2:
            print("Invalid command")
            continue
        command = user_inp[0]
        instrument = int(user_inp[1])

        if command == "S":
            await client.subscribe(instrument)
        elif command == "U":
            await client.unsubscribe(instrument)
        else:
            print("Invalid command")
            continue
if __name__ == "__main__":
    asyncio.run(main())

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server.grpc.market_data_pb2
import server.grpc.market_data_pb2_grpc
import grpc
import asyncio
import pdb
import traceback

class MarketDataClient:
    def __init__(self):
        self.channel = None
        self.stub = None
        self.subscription_queue = asyncio.Queue()
    
    def connect(self, server_address):
        with open('server.crt', 'rb') as cert_file:
            server_cert = cert_file.read()
        options = (('grpc.ssl_target_name_override', 'localhost'),)

        credentials = grpc.ssl_channel_credentials(root_certificates=server_cert)
        self.channel = grpc.aio.secure_channel(
            server_address, 
            credentials, 
            options
        )
        self.stub = server.grpc.market_data_pb2_grpc.MarketDataServiceStub(self.channel)
    
    async def run(self):
        async def request_iterator():
            while True:
                request = await self.subscription_queue.get()
                if request is None:
                    continue
                yield request

        stream = self.stub.StreamMarketData(request_iterator())
        try:
            async for response in stream:
                await self.handle_response(response)
        except Exception as e:
            print(f"Stream error {e}")
            traceback.print_exc()
        finally:
            await self.subscription_queue.put(None)
    
    async def subscribe(self, instrument_id):
        request = server.grpc.market_data_pb2.SubscriptionRequest(
            instrument_id = instrument_id,
            type = server.grpc.market_data_pb2.SubscriptionRequest.SUBSCRIBE
        )

        await self.subscription_queue.put(request)

    async def unsubscribe(self, instrument_id):
        request = server.grpc.market_data_pb2.SubscriptionRequest(
            instrument_id = instrument_id,
            type = server.grpc.market_data_pb2.SubscriptionRequest.UNSUBSCRIBE
        )

        await self.subscription_queue.put(request)
    
    async def handle_response(self, response):
        if response.type == server.grpc.market_data_pb2.MarketDataResponse.SNAPSHOT:
            self.handle_snapshot(response)
        elif response.type == server.grpc.market_data_pb2.MarketDataResponse.INCREMENTAL:
            self.handle_incremental_update(response)
        elif response.type == server.grpc.market_data_pb2.MarketDataResponse.ERROR:
            self.handle_error(response)
        else:
            self.handle_unsubscribe(response)
    
    def handle_snapshot(self, response):
        print(f"Orderbook for {response.instrument_id}")
        print("-------------")
        print("Bids")
        for level in response.orderbook_data.bids:
            print(f"${level.price}: {level.quantity} units")
        print("-------------")
        print("Asks")
        for level in response.orderbook_data.asks:
             print(f"${level.price}: {level.quantity} units")
        
    def handle_incremental_update(self, response):
        update_mappings = {
            server.grpc.market_data_pb2.OrderBookUpdate.ADD: "Adding",
            server.grpc.market_data_pb2.OrderBookUpdate.REMOVE: "Removing", 
            server.grpc.market_data_pb2.OrderBookUpdate.REPLACE: "Replacing"
        }

        bid_or_ask = "Bid" if response.update_data.is_bid else "Ask"

        print(f"{update_mappings[response.update_data.type]} Orderbook {response.instrument_id} Level on {bid_or_ask} section: Price ${response.update_data.level.price} @ {response.update_data.level.quantity} units")

    def handle_unsubscribe(self, response):
        print(f"Unsubscribing from instrument {response.instrument_id}")
    
    def handle_error(self, response):
        print(f"{response.message}")

async def main():
    client = MarketDataClient()
    client.connect('localhost:3000')

    client_task = asyncio.create_task(client.run())
    await client.subscribe(1)
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        client_task.cancel()
        await client.channel.close()  
    # try:
    #     await asyncio.sleep(5)
    #     # await client.subscribe(1)
    #     # await client.subscribe(2)

    #     # await asyncio.sleep(30)

    #     # await client.unsubscribe(1)
    #     # await client.unsubscribe(2)
    # except:
    #     print(0)
    #     # client_task.cancel()
    #     # await client.channel.close()

if __name__ == "__main__":
    asyncio.run(main())

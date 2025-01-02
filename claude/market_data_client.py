import asyncio
import grpc
import market_data_pb2
import market_data_pb2_grpc

class MarketDataClient:
    def __init__(self):
        self.orderbooks = {}  # instrument_id -> current orderbook state
        self.channel = None
        self.stub = None

    async def connect(self, server_address):
        self.channel = grpc.aio.insecure_channel(server_address)
        self.stub = market_data_pb2_grpc.MarketDataServiceStub(self.channel)

    async def run(self):
        async def request_iterator():
            while True:
                request = await self.subscription_queue.get()
                if request is None:
                    break
                yield request

        self.subscription_queue = asyncio.Queue()
        stream = self.stub.StreamMarketData(request_iterator())

        try:
            async for response in stream:
                await self.handle_response(response)
        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            await self.subscription_queue.put(None)

    async def subscribe(self, instrument_id):
        request = market_data_pb2.SubscriptionRequest(
            instrument_id=instrument_id,
            type=market_data_pb2.SubscriptionRequest.SUBSCRIBE
        )
        await self.subscription_queue.put(request)

    async def unsubscribe(self, instrument_id):
        request = market_data_pb2.SubscriptionRequest(
            instrument_id=instrument_id,
            type=market_data_pb2.SubscriptionRequest.UNSUBSCRIBE
        )
        await self.subscription_queue.put(request)

    async def handle_response(self, response):
        if response.type == market_data_pb2.MarketDataResponse.SNAPSHOT:
            # Replace entire orderbook state
            self.orderbooks[response.instrument_id] = {
                'bids': {level.price: level.quantity for level in response.data.bids},
                'asks': {level.price: level.quantity for level in response.data.asks}
            }
        elif response.type == market_data_pb2.MarketDataResponse.INCREMENT:
            # Apply incremental update
            self.apply_update(response.instrument_id, response.data)
        elif response.type == market_data_pb2.MarketDataResponse.CLEAR:
            # Clear orderbook state on unsubscribe
            if response.instrument_id in self.orderbooks:
                del self.orderbooks[response.instrument_id]

    def apply_update(self, instrument_id, update):
        # Implementation depends on your update structure
        pass

# Example usage
async def main():
    client = MarketDataClient()
    await client.connect('localhost:50051')
    
    # Start client in background
    client_task = asyncio.create_task(client.run())
    
    # Subscribe to some instruments
    await client.subscribe(1)
    await client.subscribe(2)
    
    # Wait for some updates
    await asyncio.sleep(30)
    
    # Unsubscribe
    await client.unsubscribe(1)
    await client.unsubscribe(2)
    
    # Cleanup
    client_task.cancel()
    await client.channel.close()

if __name__ == '__main__':
    asyncio.run(main())
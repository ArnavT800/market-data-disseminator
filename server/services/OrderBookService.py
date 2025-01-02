import server.grpc
import server.grpc.market_data_pb2_grpc
import server.grpc.market_data_pb2
import grpc
import concurrent
import asyncio
import collections

class OrderBookService(server.grpc.market_data_pb2_grpc.MarketDataServiceServicer):
    def __init__(self, port):
        self.port = port
        self.client_subscriptions = collections.defaultdict(set)
        self.client_queues = []
    
    async def StreamMarketData(self, request_iterator, context):
        client_address = context.peer()
        queue = asyncio.Queue()
        self.client_queues[client_address] = queue

        asyncio.create_task(self.process_subscriptions(request_iterator, client_address, context))

        try:
            while True:
                response = await queue.get()
                if not response:
                    break
                yield response
        finally:
            await self.cleanup_client(client_address)
    
    async def broadcast_update(self, update):
        if not update.action:
            return
        print(f"Broadcasting update: {update.action} level {update.level} for {update.orderbook.instrument.symbol}")

    async def broadcast_snapshot(self, snapshot, instrument):
        print(f"Snapshot for {instrument.symbol}:")
        if len(snapshot['bids']) == 0:
            print("No bids found")
        else:
            print(f"Bids: {snapshot['bids']}")
        if len(snapshot['asks']) == 0:
            print("No asks found")
        else:
            print(f"Asks: {snapshot['asks']}")
    


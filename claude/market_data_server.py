import grpc
from concurrent import futures
import asyncio
from collections import defaultdict
import market_data_pb2
import market_data_pb2_grpc

class MarketDataServicer(market_data_pb2_grpc.MarketDataServiceServicer):
    def __init__(self, orderbook_service):
        self.orderbook_service = orderbook_service
        self.client_subscriptions = defaultdict(set)
        self.client_queues = {}

    async def StreamMarketData(self, request_iterator, context):
        # Create queue for this client
        client_id = context.peer()
        queue = asyncio.Queue()
        self.client_queues[client_id] = queue

        # Start subscription handler
        asyncio.create_task(self.handle_subscriptions(request_iterator, client_id, context))

        try:
            while True:
                # Wait for data from the queue
                response = await queue.get()
                if response is None:  # Sentinel value for shutdown
                    break
                yield response
        finally:
            # Cleanup on disconnect
            await self.cleanup_client(client_id)

    async def handle_subscriptions(self, request_iterator, client_id, context):
        try:
            async for request in request_iterator:
                if request.type == market_data_pb2.SubscriptionRequest.SUBSCRIBE:
                    await self.handle_subscribe(client_id, request.instrument_id)
                else:
                    await self.handle_unsubscribe(client_id, request.instrument_id)
        except Exception as e:
            print(f"Subscription handler error: {e}")
            await self.cleanup_client(client_id)

    async def handle_subscribe(self, client_id, instrument_id):
        # Add to subscriptions
        self.client_subscriptions[client_id].add(instrument_id)
        
        # Send initial snapshot
        snapshot = self.orderbook_service.get_snapshot(instrument_id)
        response = self.create_snapshot_response(instrument_id, snapshot)
        await self.client_queues[client_id].put(response)

    async def handle_unsubscribe(self, client_id, instrument_id):
        if instrument_id in self.client_subscriptions[client_id]:
            self.client_subscriptions[client_id].remove(instrument_id)
            
            # Send clear notification
            clear_response = market_data_pb2.MarketDataResponse(
                instrument_id=instrument_id,
                type=market_data_pb2.MarketDataResponse.CLEAR
            )
            await self.client_queues[client_id].put(clear_response)

    async def cleanup_client(self, client_id):
        if client_id in self.client_queues:
            await self.client_queues[client_id].put(None)
            del self.client_queues[client_id]
        if client_id in self.client_subscriptions:
            del self.client_subscriptions[client_id]

    def broadcast_update(self, instrument_id, update):
        # Convert update to protobuf response
        response = self.create_increment_response(instrument_id, update)
        
        # Send to all subscribed clients
        for client_id, subscriptions in self.client_subscriptions.items():
            if instrument_id in subscriptions:
                asyncio.create_task(self.client_queues[client_id].put(response))

    def broadcast_snapshot(self, instrument_id):
        # Get current snapshot
        snapshot = self.orderbook_service.get_snapshot(instrument_id)
        response = self.create_snapshot_response(instrument_id, snapshot)
        
        # Send to all subscribed clients
        for client_id, subscriptions in self.client_subscriptions.items():
            if instrument_id in subscriptions:
                asyncio.create_task(self.client_queues[client_id].put(response))

    @staticmethod
    def create_snapshot_response(instrument_id, snapshot):
        return market_data_pb2.MarketDataResponse(
            instrument_id=instrument_id,
            type=market_data_pb2.MarketDataResponse.SNAPSHOT,
            data=market_data_pb2.OrderBookData(
                bids=[market_data_pb2.PriceLevel(price=p, quantity=q) 
                     for p, q in snapshot['bids']],
                asks=[market_data_pb2.PriceLevel(price=p, quantity=q) 
                     for p, q in snapshot['asks']]
            )
        )

    @staticmethod
    def create_increment_response(instrument_id, update):
        # Convert your update object to protobuf response
        pass  # Implementation depends on your update structure
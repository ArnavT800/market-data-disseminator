import grpc_files
import grpc_files.market_data_pb2_grpc
import grpc_files.market_data_pb2
import grpc
import concurrent
import asyncio
import collections
import server.globals.orderbook_mappings
import pdb

class OrderBookService(grpc_files.market_data_pb2_grpc.MarketDataServiceServicer):
    def __init__(self, port):
        self.port = port
        self.client_subscriptions = collections.defaultdict(set)
        self.client_queues = {}
    
    async def StreamMarketData(self, request_iterator, context):
        # pdb.set_trace()
        client_address = context.peer()
        queue = asyncio.Queue()
        self.client_queues[client_address] = queue

        asyncio.create_task(self.handle_subscriptions(request_iterator, client_address, context))
        try:
            while True:
                response = await queue.get()
                if response is None:
                    break
                yield response
        finally:
            await self.cleanup_client(client_address)
    
    async def handle_subscriptions(self, request_iterator, client_address, context):
        try:
            async for request in request_iterator:
                if request.type == grpc_files.market_data_pb2.SubscriptionRequest.SUBSCRIBE:
                    await self.handle_subscribe(client_address, request.instrument_id)
                else:
                    await self.handle_unsubscribe(client_address, request.instrument_id)
        except Exception as e:
            print(f"Problem with handling subscription: {e}")
            await self.cleanup_client(client_address)
    
    async def cleanup_client(self, client_address):
        if client_address in self.client_queues:
            await self.client_queues[client_address].put(None)
            del self.client_queues[client_address]
        if client_address in self.client_subscriptions:
            del self.client_subscriptions[client_address]
    
    async def handle_subscribe(self, client_address, instrument_id):
        if instrument_id in self.client_subscriptions[client_address]:
           print(f"Client {client_address} already subscribed to {instrument_id}")
           response = self.create_failure_response(client_address, instrument_id)
           await self.client_queues[client_address].put(response)
           return

        self.client_subscriptions[client_address].add(instrument_id)
        print(f"Client {client_address} successfully subscribed to {instrument_id}")
        current_orderbook_object = server.globals.orderbook_mappings.ORDERBOOKS[instrument_id]
        snapshot = current_orderbook_object.get_snapshot()

        response = self.create_snapshot_response(instrument_id, snapshot)
        await self.client_queues[client_address].put(response)
    
    async def handle_unsubscribe(self, client_address, instrument_id):
        if instrument_id not in self.client_subscriptions[client_address]:
            print(f"Client {client_address} not subscribed to {instrument_id}")
            response = self.create_failure_response(instrument_id, client_address)
            await self.client_queues[client_address].put(response)
            return
        
        self.client_subscriptions[client_address].discard(instrument_id)
        print(f"Client {client_address} successfully unsubscribed from {instrument_id}")
        response = self.create_unsub_response(instrument_id, client_address)
        await self.client_queues[client_address].put(response)

    def create_failure_response(self, instrument_id, client_address):
        error_message = grpc_files.market_data_pb2.ErrorResponse(
            error = f"Subscription/unsubscription mechanism failed for {client_address} to {instrument_id}"
        )
        return grpc_files.market_data_pb2.MarketDataResponse(
            instrument_id = instrument_id,
            type = grpc_files.market_data_pb2.MarketDataResponse.ERROR,
            message = error_message
        )
    
    def create_snapshot_response(self, instrument_id, snapshot):
        return grpc_files.market_data_pb2.MarketDataResponse(
            instrument_id = instrument_id,
            type = grpc_files.market_data_pb2.MarketDataResponse.SNAPSHOT,
            orderbook_data = grpc_files.market_data_pb2.OrderBookData(
                bids = [
                    grpc_files.market_data_pb2.Level(price = price, quantity = quantity)
                    for price, quantity in snapshot['bids']
                ],
                asks = [
                    grpc_files.market_data_pb2.Level(price = price, quantity = quantity)
                    for price, quantity in snapshot['asks']
                ]
            ),
            message = f"New snapshot for {instrument_id}"
        )
    
    def create_incremental_update_response(self, instrument_id, update):
        update_mappings = {
            "Adding": grpc_files.market_data_pb2.OrderBookUpdate.ADD,
            "Removing": grpc_files.market_data_pb2.OrderBookUpdate.REMOVE,
            "Replacing": grpc_files.market_data_pb2.OrderBookUpdate.REPLACE
        }

        return grpc_files.market_data_pb2.MarketDataResponse(
            instrument_id = instrument_id,
            type = grpc_files.market_data_pb2.MarketDataResponse.INCREMENTAL,
            update_data = grpc_files.market_data_pb2.OrderBookUpdate(
                type = update_mappings[update.action],
                is_bid = update.is_bid,
                level = grpc_files.market_data_pb2.Level(
                    price = update.level.price,
                    quantity = update.level.quantity
                )
            )
        )
    
    def create_unsub_response(self, instrument_id, client_address):
        unsubscribe_message = f"Client {client_address} successfully unsubscribed from instrument {instrument_id}"
        return grpc_files.market_data_pb2.MarketDataResponse(
            instrument_id = instrument_id,
            type = grpc_files.market_data_pb2.MarketDataResponse.UNSUBSCRIBE,
            message = unsubscribe_message
        )

    async def broadcast_update(self, update):
        if not update.action:
            return
        
        streaming_instrument_id = update.orderbook.instrument.id
        response = self.create_incremental_update_response(streaming_instrument_id, update)
        for client_address, subscriptions in self.client_subscriptions.items():
            if streaming_instrument_id in subscriptions:
                try:
                    await self.client_queues[client_address].put(response)
                except Exception as e:
                    print(f"Failed streaming updates for instrument {streaming_instrument_id} to client {client_address}: {e}") 

            
    async def broadcast_snapshot(self, snapshot, instrument):
        response = self.create_snapshot_response(instrument.id, snapshot)
        for client_address, subscriptions in self.client_subscriptions.items():
            if instrument.id in subscriptions:
                try: 
                    await self.client_queues[client_address].put(response)
                except Exception as e:
                    print(f"Failed streaming snapshot for instrument {instrument.id} to client {client_address}: {e}") 
    
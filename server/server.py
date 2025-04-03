import server.globals.orderbook_mappings
from server.services.parser import load_data
from server.services.OrderBookService import OrderBookService
from server.models.OrderBook import OrderBook
import server.globals
import grpc
import grpc_files.market_data_pb2_grpc
import asyncio

class Server:
    def __init__(self, config_path):
        self.orderbooks = {}
        self.service = None
        self.config_path = config_path
        self.grpc_server = None

    async def start(self):
        print("Starting server...")
        config = load_data(self.config_path)
        self.service = OrderBookService(config[0])

        self.grpc_server = grpc.aio.server()
        grpc_files.market_data_pb2_grpc.add_MarketDataServiceServicer_to_server(self.service, self.grpc_server)
        server_address = 'localhost:3000'

        with open('server/server.crt', 'rb') as cert_file:
            certificate_chain = cert_file.read()
        
        with open('server/server.key', 'rb') as key_file:
            private_key = key_file.read()

        credentials = grpc.ssl_server_credentials(
            [(private_key, certificate_chain)]
        )
        self.grpc_server.add_secure_port(server_address, credentials)
        await self.grpc_server.start()
        print(f"gRPC server listening on {server_address}")


        for instrument in config[1]:
            orderbook = OrderBook(instrument, self.service)
            self.orderbooks[instrument.id] = orderbook

            server.globals.orderbook_mappings.ORDERBOOKS[instrument.id] = orderbook
            
            await orderbook.start()
    
    def get_snapshot(self, instrument_id):
        if instrument_id not in self.orderbooks:
            raise KeyError(f"Orderbook {instrument_id} not found")
        return self.orderbooks[instrument_id].get_snapshot()
    
    async def dispose(self):
        print("Closing server...")
        for orderbook in self.orderbooks.values():
            orderbook.dispose()
        self.orderbooks.clear()
        print("stopping grpc")
        await self.grpc_server.stop(grace=True)
        await asyncio.sleep(1)

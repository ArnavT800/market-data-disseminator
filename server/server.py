import server.globals.orderbook_mappings
from server.services.parser import load_data
from server.services.OrderBookService import OrderBookService
from server.models.OrderBook import OrderBook
import server.globals

class Server:
    def __init__(self, config_path):
        self.orderbooks = {}
        self.service = None
        self.config_path = config_path

    async def start(self):
        print("Starting server...")
        config = load_data(self.config_path)
        self.service = OrderBookService(config[0])

        for instrument in config[1]:
            orderbook = OrderBook(instrument, self.service)
            self.orderbooks[instrument.id] = orderbook

            server.globals.orderbook_mappings[instrument.id] = orderbook
            
            await orderbook.start()
    
    def get_snapshot(self, instrument_id):
        if instrument_id not in self.orderbooks:
            raise KeyError(f"Orderbook {instrument_id} not found")
        return self.orderbooks[instrument_id].get_snapshot()
    
    def dispose(self):
        print("Closing server...")
        for orderbook in self.orderbooks.values():
            orderbook.dispose()
        self.orderbooks.clear()

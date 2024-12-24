from parser import load_data
from OrderBookManager import OrderBookManager

import asyncio
class Server:
    def __init__(self, config_path):
        data = load_data(config_path)
        self.instruments = data[1]
        self.orderbooks = {} # Dict<int, OrderBook> 
        for instrument in self.instruments:
            self.orderbooks[instrument.id] = instrument
        self.orderbook_manager = OrderBookManager(self.instruments)
        self.running = True
    
    async def get_snapshot(self, instrument_id):
        orderbook = self.orderbooks.get(instrument_id)
        if not orderbook:
            raise KeyError(f"Orderbook {instrument_id} not present")
        return await orderbook.get_snapshot()

    async def start(self):
        print("Starting server...")
        await asyncio.gather(
            self.orderbook_manager.start(),
            self.disseminate_data()
        )

    async def disseminate_data(self):
        try:
            while self.running:
                await self.orderbook_manager.upload_snapshots()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Dissemination Failed")

    async def stop(self):
        print("Stopping Server...")
        self.running = False

import collections
import random
import asyncio
from server.services.OrderBookUpdate import OrderBookUpdate

class OrderBook:
    def __init__(self, instrument, service):
        self.instrument = instrument
        self.service = service
        self.depth = instrument.orderbook_depth
        self.bids = collections.OrderedDict()
        self.asks = collections.OrderedDict()
        self.disposed = False
        self.task = None

    async def generate_updates(self):
        while not self.disposed:
            try:
                await asyncio.sleep(random.random() * 2)

                if random.random() > 0.95:
                    snapshot = self.get_snapshot()
                    await self.service.broadcast_snapshot(snapshot, self.instrument)
                else:
                    update = OrderBookUpdate(self, self.depth)
                    update.update()
                    await self.service.broadcast_update(update)
                
            except Exception as ex:
                print(f"Failed to update orderbook, {update}: {ex}")

    async def start(self):
        self.task = asyncio.create_task(self.generate_updates())
        
    def get_snapshot(self):
        return {
            'bids': [(level.price, level.quantity) for level in self.bids.values()],
            'asks': [(level.price, level.quantity) for level in self.asks.values()]
        }

    def dispose(self):
        self.disposed = True
        if self.task:
            self.task.cancel()

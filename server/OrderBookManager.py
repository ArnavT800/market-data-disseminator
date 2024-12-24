import asyncio
from OrderBook import OrderBook

class OrderBookManager:
    def __init__(self, orderbooks):
        self.orderbooks = orderbooks
    
    async def upload_snapshots(self):
        for orderbook in self.orderbooks:
            await orderbook.upload_snapshot
            asyncio.sleep(1)
    
    
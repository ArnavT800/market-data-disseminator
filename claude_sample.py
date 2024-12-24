import json
import asyncio
import random
from dataclasses import dataclass
from typing import Dict, List, Optional
from collections import OrderedDict

@dataclass
class Specifications:
    depth: int

@dataclass
class Instrument:
    id: int
    symbol: str
    specifications: Specifications

class OrderbookLevel:
    def __init__(self, price: float, quantity: int):
        self.price = price
        self.quantity = quantity

class OrderbookUpdate:
    def __init__(self, instrument_id: int, update_type: str, level: OrderbookLevel, is_bid: bool):
        self.instrument_id = instrument_id
        self.update_type = update_type  # 'add', 'remove', 'replace'
        self.level = level
        self.is_bid = is_bid

class Orderbook:
    def __init__(self, instrument: Instrument, service):
        self.instrument = instrument
        self.service = service
        self.bids = OrderedDict()  # price -> OrderbookLevel
        self.asks = OrderedDict()  # price -> OrderbookLevel
        self._disposed = False
        self.task = None

    async def start(self):
        self.task = asyncio.create_task(self._generate_updates())

    async def _generate_updates(self):
        while not self._disposed:
            try:
                await asyncio.sleep(random.random() * 2)  # Random delay between updates
                
                # Randomly choose between bid and ask update
                is_bid = random.choice([True, False])
                levels = self.bids if is_bid else self.asks
                
                # Calculate probability of removal based on current depth
                removal_prob = len(levels) / (self.instrument.specifications.depth + 1)
                
                if len(levels) >= self.instrument.specifications.depth:
                    # Must remove or replace when at max depth
                    if random.random() < 0.5:
                        await self._remove_level(is_bid)
                    else:
                        await self._replace_level(is_bid)
                else:
                    # Choose between add, remove, or replace
                    if random.random() < removal_prob:
                        await self._remove_level(is_bid)
                    elif random.random() < 0.3:
                        await self._replace_level(is_bid)
                    else:
                        await self._add_level(is_bid)
                        
            except Exception as ex:
                print(f"Failed to generate orderbook update: {ex}")

    async def _add_level(self, is_bid: bool):
        price = self._generate_price(is_bid)
        quantity = random.randint(1, 1000)
        level = OrderbookLevel(price, quantity)
        
        levels = self.bids if is_bid else self.asks
        levels[price] = level
        
        update = OrderbookUpdate(self.instrument.id, 'add', level, is_bid)
        await self.service.broadcast_update(update)

    async def _remove_level(self, is_bid: bool):
        levels = self.bids if is_bid else self.asks
        if not levels:
            return
            
        price = random.choice(list(levels.keys()))
        level = levels.pop(price)
        
        update = OrderbookUpdate(self.instrument.id, 'remove', level, is_bid)
        await self.service.broadcast_update(update)

    async def _replace_level(self, is_bid: bool):
        levels = self.bids if is_bid else self.asks
        if not levels:
            return
            
        price = random.choice(list(levels.keys()))
        level = OrderbookLevel(price, random.randint(1, 1000))
        levels[price] = level
        
        update = OrderbookUpdate(self.instrument.id, 'replace', level, is_bid)
        await self.service.broadcast_update(update)

    def _generate_price(self, is_bid: bool) -> float:
        # Generate a price that maintains bid-ask spread
        base = 100  # Base price
        spread = 0.1  # Minimum spread
        
        if is_bid:
            max_bid = min(self.asks.keys()) - spread if self.asks else float('inf')
            return random.uniform(base - 10, min(base, max_bid))
        else:
            min_ask = max(self.bids.keys()) + spread if self.bids else float('-inf')
            return random.uniform(max(base, min_ask), base + 10)

    def get_snapshot(self):
        return {
            'bids': [(level.price, level.quantity) for level in self.bids.values()],
            'asks': [(level.price, level.quantity) for level in self.asks.values()]
        }

    def dispose(self):
        self._disposed = True
        if self.task:
            self.task.cancel()

class OrderbookService:
    def __init__(self, port: int):
        self.port = port
        self.clients = set()
        
    async def broadcast_update(self, update: OrderbookUpdate):
        # In a real implementation, this would send updates to connected clients
        # For now, we'll just print the updates
        print(f"Broadcasting update: {update.__dict__}")

class Server:
    def __init__(self, config_path: str):
        self.orderbooks: Dict[int, Orderbook] = {}
        self.service = None
        self.config_path = config_path

    async def start(self):
        # Read configuration
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        # Initialize service
        self.service = OrderbookService(config['Port'])
        
        # Create orderbooks for each instrument
        for instr_config in config['Instruments']:
            instrument = Instrument(
                id=instr_config['Id'],
                symbol=instr_config['Symbol'],
                specifications=Specifications(instr_config['Specifications']['Depth'])
            )
            
            orderbook = Orderbook(instrument, self.service)
            self.orderbooks[instrument.id] = orderbook
            await orderbook.start()

    def get_snapshot(self, instrument_id: int):
        if instrument_id not in self.orderbooks:
            raise KeyError(f"Orderbook {instrument_id} does not exist.")
        return self.orderbooks[instrument_id].get_snapshot()

    def dispose(self):
        for orderbook in self.orderbooks.values():
            orderbook.dispose()
        self.orderbooks.clear()

# Example usage
async def main():
    server = Server('appsettings.json')
    await server.start()
    
    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        server.dispose()

if __name__ == "__main__":
    asyncio.run(main())
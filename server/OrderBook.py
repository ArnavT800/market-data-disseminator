import collections
import random
import asyncio

class OrderBook:
    def __init__(self, instrument):
        self.instrument = instrument
        self.bids = collections.deque(maxlen=self.instrument.depth)
        self.asks = collections.deque(maxlen=self.instrument.depth)

    async def generate_updates(self, instrument):
        
        while True:
            await asyncio.sleep(random.uniform(0.1, 2))
            action = random.choice(["add", "remove", "replace"])
            if action == "add":
                self.add_level()
            elif action == "remove":
                self.remove_level()
            else:
                self.replace_level()
    
    def add_level(self):
        price = random.uniform(100, 200)
        quantity = random.randint(1, 1000)
        

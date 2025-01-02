import random
from server.models.OrderBookLevel import OrderBookLevel

class OrderBookUpdate:
    def __init__(self, orderbook, depth):
        self.orderbook = orderbook
        self.depth = depth
        self.is_bid = random.choice([True, False])
        self.entries = orderbook.bids if self.is_bid else orderbook.asks
        self.action = None # ["add", "replace", "remove"]
        self.level = None

    def __str__(self):
        return f"{self.entries}, {self.depth}, {self.action}"

    def update(self):
        if len(self.entries) >= self.depth:
            if random.random() < 0.5:
                self.remove_level()
            else:
                self.replace_level()
        else:
            removal_prob = len(self.entries) / (self.depth + 1)
            if random.random() < removal_prob:
                self.remove_level()
            elif random.random() < 0.3:
                self.replace_level()
            else:
                self.add_level()
    
    def generate_price(self):
        base_price = 100
        spread = 0.1

        if self.is_bid:
            max_bid = min(self.orderbook.asks.keys()) - spread if self.orderbook.asks else float('inf')
            return round(random.uniform(base_price - 10, min(base_price, max_bid)), 2)
        else:
            min_ask = max(self.orderbook.bids.keys()) + spread if self.orderbook.bids else float('-inf')
            return round(random.uniform(max(base_price, min_ask), base_price + 10), 2)
        
    def remove_level(self):
        if len(self.entries) == 0:
            return
        price_point = random.choice(list(self.entries.keys()))
        self.level = self.entries.pop(price_point)
        self.action = "Removing"

    def replace_level(self):
        if len(self.entries) == 0:
            return
        price = random.choice(list(self.entries.keys()))
        self.level = OrderBookLevel(price, random.randint(1, 1000))
        self.entries[price] = self.level
        self.action = "Replacing"
    
    def add_level(self):
        price = self.generate_price()
        quantity = random.randint(1, 1000)
        level = OrderBookLevel(price, quantity)

        self.entries[price] = level
        self.level = level
        self.action = "Adding" 
    
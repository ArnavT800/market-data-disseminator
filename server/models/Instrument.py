class Instrument:
    def __init__(self, id, symbol, orderbook_depth):
        self.id = id
        self.symbol = symbol
        self.orderbook_depth = orderbook_depth
    def __repr__(self):
        return f"Instrument(id = {self.id}), symbol = {self.symbol}, orderbook_depth = {self.orderbook_depth})"

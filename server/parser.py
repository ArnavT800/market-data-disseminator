import json

class Instrument:
    def __init__(self, instrument_id, symbol, orderbook_depth):
        self.id = instrument_id
        self.symbol = symbol
        self.depth = orderbook_depth
    def __repr__(self):
        return f"Instrument(id = {self.id}), symbol = {self.symbol}, orderbook_depth = {self.depth})"

def load_data(config_path):
    with open(config_path, "r") as file:
        data = json.load(file)
    port = data['Port']
    instruments = []
    for instrument in data['Instruments']:
        instruments.append(Instrument(
            instrument_id=instrument['Id'],
            symbol = instrument['Symbol'],
            orderbook_depth = instrument['Specs']['OrderBookDepth']
        ))
    return [port, instruments]
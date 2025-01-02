import json
from server.models.Instrument import Instrument

def load_data(config_path):
    with open(config_path, "r") as file:
        data = json.load(file)
    port = data['Port']
    instruments = []
    for instrument in data['Instruments']:
        instruments.append(Instrument(
            id=instrument['Id'],
            symbol = instrument['Symbol'],
            orderbook_depth = instrument['Specs']['OrderBookDepth']
        ))
    return [port, instruments]
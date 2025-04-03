import grpc
import market_data_pb2
import market_data_pb2_grpc
import asyncio
import collections
import concurrent

class MarketDataServicer(market_data_pb2_grpc.MarketDataServiceServicer):
    def __init__(self, orderbook_service):
        self.orderbook_service = orderbook_service
# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: market_data.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'market_data.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11market_data.proto\x12\nmarketdata\"\x96\x01\n\x13SubscriptionRequest\x12\x15\n\rinstrument_id\x18\x01 \x01(\x05\x12\x39\n\x04type\x18\x02 \x01(\x0e\x32+.marketdata.SubscriptionRequest.RequestType\"-\n\x0bRequestType\x12\r\n\tSUBSCRIBE\x10\x00\x12\x0f\n\x0bUNSUBSCRIBE\x10\x01\"(\n\x05Level\x12\r\n\x05price\x18\x01 \x01(\x02\x12\x10\n\x08quantity\x18\x02 \x01(\x05\"Q\n\rOrderBookData\x12\x1f\n\x04\x62ids\x18\x01 \x03(\x0b\x32\x11.marketdata.Level\x12\x1f\n\x04\x61sks\x18\x02 \x03(\x0b\x32\x11.marketdata.Level\"\xa7\x02\n\x12MarketDataResponse\x12\x15\n\rinstrument_id\x18\x01 \x01(\x05\x12\x39\n\x04type\x18\x02 \x01(\x0e\x32+.marketdata.MarketDataResponse.ResponseType\x12\x31\n\x0eorderbook_data\x18\x03 \x01(\x0b\x32\x19.marketdata.OrderBookData\x12\x30\n\x0bupdate_data\x18\x04 \x01(\x0b\x32\x1b.marketdata.OrderBookUpdate\x12\x0f\n\x07message\x18\x05 \x01(\t\"I\n\x0cResponseType\x12\x0c\n\x08SNAPSHOT\x10\x00\x12\x0f\n\x0bINCREMENTAL\x10\x01\x12\t\n\x05\x45RROR\x10\x02\x12\x0f\n\x0bUNSUBSCRIBE\x10\x03\"\xa9\x01\n\x0fOrderBookUpdate\x12\x34\n\x04type\x18\x01 \x01(\x0e\x32&.marketdata.OrderBookUpdate.UpdateType\x12\x0e\n\x06is_bid\x18\x02 \x01(\x08\x12 \n\x05level\x18\x03 \x01(\x0b\x32\x11.marketdata.Level\".\n\nUpdateType\x12\x07\n\x03\x41\x44\x44\x10\x00\x12\x0b\n\x07REPLACE\x10\x01\x12\n\n\x06REMOVE\x10\x02\x32l\n\x11MarketDataService\x12W\n\x10StreamMarketData\x12\x1f.marketdata.SubscriptionRequest\x1a\x1e.marketdata.MarketDataResponse(\x01\x30\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'market_data_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SUBSCRIPTIONREQUEST']._serialized_start=34
  _globals['_SUBSCRIPTIONREQUEST']._serialized_end=184
  _globals['_SUBSCRIPTIONREQUEST_REQUESTTYPE']._serialized_start=139
  _globals['_SUBSCRIPTIONREQUEST_REQUESTTYPE']._serialized_end=184
  _globals['_LEVEL']._serialized_start=186
  _globals['_LEVEL']._serialized_end=226
  _globals['_ORDERBOOKDATA']._serialized_start=228
  _globals['_ORDERBOOKDATA']._serialized_end=309
  _globals['_MARKETDATARESPONSE']._serialized_start=312
  _globals['_MARKETDATARESPONSE']._serialized_end=607
  _globals['_MARKETDATARESPONSE_RESPONSETYPE']._serialized_start=534
  _globals['_MARKETDATARESPONSE_RESPONSETYPE']._serialized_end=607
  _globals['_ORDERBOOKUPDATE']._serialized_start=610
  _globals['_ORDERBOOKUPDATE']._serialized_end=779
  _globals['_ORDERBOOKUPDATE_UPDATETYPE']._serialized_start=733
  _globals['_ORDERBOOKUPDATE_UPDATETYPE']._serialized_end=779
  _globals['_MARKETDATASERVICE']._serialized_start=781
  _globals['_MARKETDATASERVICE']._serialized_end=889
# @@protoc_insertion_point(module_scope)

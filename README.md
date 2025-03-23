# Market Data Streaming Application

This repository implements a gRPC-based **Market Data Streaming Application** written in asynchronous Python. It provides a client-server architecture for simulating and handling market data order books with streaming updates
to clients via a subscription mechanism.

## Features

- **Server-Side**: 
  - Simulates market data updates for instruments.
  - Maintains order books for multiple instruments.
  - Sends real-time order book snapshots and incremental updates to subscribed clients.
- **Client-Side**: 
  - Allows subscription and unsubscription to instruments.
  - Processes real-time market data streams.
- **Protocol Buffers**:
  - Defines the gRPC communication protocol for subscription requests and market data responses.

## Setup

#### Prequisites
Run `pip install -r requirements.txt`

#### Starting the Server
`python main.py`

#### Starting the client
`python client/client.py`

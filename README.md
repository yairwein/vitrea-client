# Vitrea Client (Python)

> Python client library for Vitrea Smart Home API

**This is a Python port of the original TypeScript [vitrea-client](https://github.com/bdsoha/vitrea-client) library by [bdsoha](https://github.com/bdsoha). Full credit goes to the original author for the protocol implementation and API design.**

---

## Requirements

Python 3.8+ is required to use this package.

## Installation

```bash
pip install vitrea-client
```

Or using uv:

```bash
uv add vitrea-client
```

## Configurations

The section below outlines the different configuration values available and their
corresponding default settings.

| Config                              | Description                                               | Default              |
| ----------------------------------- | --------------------------------------------------------- | -------------------- |
| `ConnectionConfig.host`             | Host address to connect to the vBox                       | `192.168.1.23`       |
| `ConnectionConfig.port`             | Port used to connect to the vBox                          | `11501`              |
| `ConnectionConfig.username`         | Username used to connect to the vBox                      | `None`               |
| `ConnectionConfig.password`         | Password used to connect to the vBox                      | `None`               |
| `ConnectionConfig.protocol_version` | Protocol version of vBox                                  | `ProtocolVersion.V2` |
| `SocketConfig.logger`               | Logger to print values                                    | `None`               |
| `SocketConfig.ignore_ack_logs`      | Ignore `Acknowledgement` and `GenericUnusedResponse` logs | `False`              |
| `SocketConfig.request_buffer`       | Buffer time between requests (seconds)                    | `0.25`               |
| `SocketConfig.request_timeout`      | Max timeout for requests (seconds)                       | `1.0`                |
| `SocketConfig.should_reconnect`     | Automatically reconnect on lost connection                | `True`               |

### Environment Variables

If you prefer not to provide the configuration values directly, you can use environment
variables instead.

All `ConnectionConfig` configuration values can be represented as environment variables by
converting the config key to uppercase and prefixing it with `VITREA_VBOX_`.
For instance, the key `username` would be represented as `VITREA_VBOX_USERNAME` and
`request_timeout` as `VITREA_VBOX_REQUEST_TIMEOUT`.

## Usage

```python
import asyncio
from vitrea_client import VitreaClient, ProtocolVersion
from vitrea_client.requests import RoomCount, KeyStatus, ToggleKeyStatus
from vitrea_client.utilities.enums import KeyPowerStatus

async def main():
    # Create client with configuration
    client = VitreaClient.create(
        connection_config={
            'host': '192.168.1.111',
            'port': 1234,
            'username': 'admin',
            'password': 'secret',
            'protocol_version': ProtocolVersion.V1
        }
    )
    
    # Connect to the vBox
    await client.connect()
    
    # Send a request and get response
    room_count_response = await client.send(RoomCount())
    print(f"Number of rooms: {room_count_response.count}")
    
    # Use convenience methods
    room_count = await client.get_room_count()
    node_count = await client.get_node_count()
    
    # Control a key
    await client.turn_key_on(node_id=1, key_id=2)
    await client.turn_key_off(node_id=1, key_id=2)
    
    # Get key status
    key_status = await client.get_key_status(node_id=1, key_id=2)
    print(f"Key is {'on' if key_status.is_on() else 'off'}")
    
    # Disconnect when done
    await client.disconnect()

# Run the async function
asyncio.run(main())
```

### Logging

By default, all logs are sent to the `NullLogger`, which discards them.
To log messages, you can use our `ConsoleLogger`:

```python
from vitrea_client import VitreaClient
from vitrea_client.core.logger import ConsoleLogger

client = VitreaClient.create(
    connection_config={'host': '192.168.1.111'},
    socket_config={'logger': ConsoleLogger()}
)
```

If you already have a logger that implements the `LoggerProtocol` interface, you can integrate it:

```python
from vitrea_client import VitreaClient
from vitrea_client.core.logger import LoggerProtocol

class MyLogger(LoggerProtocol):
    def log(self, message: str, level: str) -> None:
        # Your logging implementation
        pass
    
    def error(self, message: str, *args) -> None:
        # Your error logging implementation
        pass
    
    def warn(self, message: str, *args) -> None:
        # Your warning logging implementation
        pass
    
    def info(self, message: str, *args) -> None:
        # Your info logging implementation
        pass
    
    def debug(self, message: str, *args) -> None:
        # Your debug logging implementation
        pass

client = VitreaClient.create(
    connection_config={'host': '192.168.1.111'},
    socket_config={'logger': MyLogger()}
)
```

### Status Updates

Vitrea's vBox sends updates to the client whenever a key is pressed.
You can supply a custom callback listener to manage these updates as they happen.

```python
from vitrea_client import VitreaClient
from vitrea_client.responses import KeyStatus

async def main():
    client = VitreaClient.create(...)
    
    def key_status_listener(status: KeyStatus):
        print(f"Node ID: {status.node_id}")
        print(f"Key ID: {status.key_id}")
        print(f"Power Status: {'On' if status.is_on() else 'Off'}")
        print(f"Is Released: {status.is_released()}")
    
    # Register the callback
    client.on_key_status(key_status_listener)
    
    await client.connect()
    # Now the callback will be called whenever key status updates are received
    
    # Keep the connection alive to receive updates
    await asyncio.sleep(30)
    
    await client.disconnect()

asyncio.run(main())
```

## API Reference

### VitreaClient

The main client class for interacting with the Vitrea vBox.

#### Methods

- `create(connection_config=None, socket_config=None)` - Create a new VitreaClient instance
- `connect()` - Connect to the vBox
- `disconnect()` - Disconnect from the vBox
- `send(request)` - Send a request and wait for response
- `on_key_status(callback)` - Register a callback for key status updates

#### Convenience Methods

- `get_room_count()` - Get the number of rooms
- `get_node_count()` - Get the number of nodes
- `get_room_metadata(room_id)` - Get metadata for a specific room
- `get_node_metadata(node_id)` - Get metadata for a specific node
- `get_key_status(node_id, key_id)` - Get status of a specific key
- `get_key_parameters(node_id, key_id)` - Get parameters of a specific key
- `turn_key_on(node_id, key_id, timer=None, dimmer_ratio=None)` - Turn a key on
- `turn_key_off(node_id, key_id)` - Turn a key off
- `release_key(node_id, key_id)` - Release a key
- `toggle_key(node_id, key_id, power_status, timer=None, dimmer_ratio=None)` - Toggle key state
- `send_heartbeat()` - Send a heartbeat request

### Request Classes

All request classes are available in `vitrea_client.requests`:

- `RoomCount` - Get room count
- `NodeCount` - Get node count
- `RoomMetaData(room_id)` - Get room metadata
- `NodeMetaData(node_id)` - Get node metadata
- `KeyStatus(node_id, key_id)` - Get key status
- `KeyParameters(node_id, key_id)` - Get key parameters
- `NodeStatus(node_id)` - Get node status
- `InternalUnitStatuses()` - Get internal unit statuses
- `Login(username, password)` - Login to vBox
- `ToggleKeyStatus(node_id, key_id, power_status, timer=None, dimmer_ratio=None)` - Toggle key
- `ToggleHeartbeat(enabled)` - Toggle heartbeat
- `Heartbeat()` - Send heartbeat

### Response Classes

All response classes are available in `vitrea_client.responses`:

- `RoomCount` - Room count response
- `NodeCount` - Node count response
- `RoomMetaData` - Room metadata response
- `NodeMetaData` - Node metadata response
- `KeyStatus` - Key status response
- `KeyParameters` - Key parameters response
- `Acknowledgement` - Acknowledgement response
- `InternalUnitStatuses` - Internal unit statuses response
- `GenericUnusedResponse` - Generic unused response

## Development

This project uses `uv` for dependency management and `pytest` for testing.

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd vitrea-client

# Install dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ -v --cov=src/vitrea_client --cov-report=term-missing
```

### Testing

The project includes comprehensive tests covering:

- Core data structures and protocols
- Request and response serialization
- Socket communication
- Client functionality
- Integration scenarios

Run the test suite:

```bash
uv run pytest tests/ -v
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

This Python implementation is based on the original TypeScript [vitrea-client](https://github.com/bdsoha/vitrea-client) library by [bdsoha](https://github.com/bdsoha). The protocol implementation, API design, and overall architecture are derived from that excellent work.

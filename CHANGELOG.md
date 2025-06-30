# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-19

### Added
- Complete Python port of the TypeScript [vitrea-client](https://github.com/bdsoha/vitrea-client) library
- Full async/await support using asyncio
- Comprehensive logging system with LoggerProtocol, ConsoleLogger, and NullLogger
- Core data structures: DataGram, BaseRequest, BaseResponse
- Complete request/response protocol implementation:
  - 13 request classes (RoomCount, NodeMetaData, KeyStatus, Login, ToggleKeyStatus, etc.)
  - 11 response classes with proper data parsing and validation
  - ResponseFactory for automatic response object creation
- Socket communication layer with:
  - TCP connection management
  - Automatic reconnection support
  - Heartbeat mechanism
  - Timeout handling
  - Buffer splitting for multiple datagrams
- Main VitreaClient with convenience methods:
  - `get_room_count()`, `get_node_count()`
  - `get_room_metadata()`, `get_node_metadata()`
  - `get_key_status()`, `get_key_parameters()`
  - `turn_key_on()`, `turn_key_off()`, `release_key()`
  - `toggle_key()`, `send_heartbeat()`
- Event-driven status update callbacks with `on_key_status()`
- Configuration system with environment variable support
- Custom exceptions: ConnectionExistsException, NoConnectionException, TimeoutException
- Comprehensive utilities: Enums, MessageID, Events
- Full test suite with 186 tests and 85% code coverage
- Complete documentation and usage examples

### Technical Details
- Built with Python 3.8+ support
- Uses asyncio for asynchronous operations
- Protocol-compatible with original TypeScript implementation
- Maintains same API design patterns and naming conventions
- Includes both V1 and V2 protocol version support
- UTF-16LE encoding support for login credentials and room names
- Proper checksum validation and binary data handling

### Credits
This Python implementation is a complete port of the original TypeScript [vitrea-client](https://github.com/bdsoha/vitrea-client) library by [bdsoha](https://github.com/bdsoha). All protocol implementation, API design, and architecture concepts are derived from that excellent work. 
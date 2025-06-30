# Python Porting Plan for vitrea-client

This document outlines the plan to create a Python version of the `vitrea-client` TypeScript library. The plan is broken down into incremental and testable steps.

## Step 1: Project Setup and Core Components

The goal of this step is to set up the basic project structure and implement the core, non-network-dependent components.

- **1.1: Project Structure**:
  - Create a `pyproject.toml` for project metadata and dependencies (e.g., using Poetry or Hatch).
  - Create a `src/vitrea_client` directory for the Python source code.
  - Set up a testing framework (e.g., `pytest`).

- **1.2: Logging**:
  - Define a `Logger` protocol (similar to `LoggerContract`).
  - Implement a `ConsoleLogger` and a `NullLogger`.
  - **Test**: Write tests to verify that loggers can be instantiated and their methods called.

- **1.3: Core Data Structures**:
  - Implement the `DataGram` class for handling the low-level data format.
  - Implement `BaseRequest` and `BaseResponse` abstract base classes.
  - **Test**: Write unit tests for `DataGram` serialization/deserialization. Test that `BaseRequest` and `BaseResponse` cannot be instantiated directly.

- **1.4: Exceptions**:
  - Create custom exception classes (e.g., `ConnectionExistsException`, `NoConnectionException`, `TimeoutException`).
  - **Test**: Write simple tests to ensure exceptions can be raised.

- **1.5: Configuration**:
  - Implement configuration classes for VBox and Socket settings.
  - Implement parsers that can read from environment variables (e.g., `os.getenv`).
  - **Test**: Write tests to verify that configuration is correctly parsed from direct input and environment variables.

## Step 2: Implementing the Communication Protocol

This step focuses on implementing all the request and response classes, which form the core of the vBox communication protocol.

- **2.1: Implement Request Classes**:
  - Create Python classes for each request type found in the `requests` directory (e.g., `RoomCount`, `NodeStatus`, `Login`).
  - These classes will inherit from `BaseRequest` and implement the required serialization logic.
  - **Test**: For each request class, write a unit test to verify it serializes to the correct `DataGram` format.

- **2.2: Implement Response Classes**:
  - Create Python classes for each response type from the `responses` directory (e.g., `RoomCount`, `NodeMetaData`, `KeyStatus`).
  - These classes will inherit from `BaseResponse`.
  - Implement `ResponseCodes` as an Enum.
  - **Test**: Write unit tests for each response class to verify they can be created from a `DataGram`.

- **2.3: Implement Response Factory**:
  - Create a `ResponseFactory` that takes a raw `DataGram` and returns the appropriate response object based on the response code.
  - This is a critical component for handling incoming data.
  - **Test**: Write extensive tests for the `ResponseFactory` to ensure it correctly maps all response codes to the right response classes.

## Step 3: Socket Communication and Connection Management

This step deals with the networking layer, connecting to the vBox and managing the communication flow.

- **3.1: Socket Abstraction**:
  - Create a socket handling class (e.g., `VitreaSocket`) that uses Python's built-in `socket` or `asyncio` streams.
  - This class will manage connecting, disconnecting, sending, and receiving data.

- **3.2: Heartbeat Mechanism**:
  - Implement the heartbeat handler to send periodic heartbeat requests to keep the connection alive.

- **3.3: Request/Response Flow**:
  - Implement the logic to send a request and wait for a corresponding response.
  - Handle timeouts if a response is not received within a certain period.

- **3.4: Reconnection Logic**:
  - Add automatic reconnection capabilities to the socket class.

- **3.5: Testing with a Mock Server**:
  - **Test**: Create a simple mock TCP server that can accept connections and send pre-defined responses. Write integration tests for the socket class against this mock server to test connection, sending requests, receiving responses, timeouts, and reconnection.

## Step 4: The Main `VitreaClient`

This final step brings all the components together into a user-friendly client class.

- **4.1: `VitreaClient` Implementation**:
  - Create the main `VitreaClient` class.
  - It will instantiate and manage the socket connection.
  - It will provide the public API: `connect()`, `disconnect()`, `send(request)`.

- **4.2: Status Update Callbacks**:
  - Implement the `on_key_status` method for registering a callback function.
  - The client should parse incoming key status updates and invoke the callback.

- **4.3: Integration Testing**:
  - **Test**: Write integration tests for the `VitreaClient` using the mock server. Test the full lifecycle: connect, send a request, receive a response, receive an unsolicited status update, and disconnect.

## Step 5: Documentation and Packaging

- **5.1: README**:
  - Write a `README.md` file for the Python package with installation and usage instructions, similar to the original library.

- **5.2: Final Packaging**:
  - Prepare the package for publishing to PyPI.
  - Ensure all necessary files are included in the distribution. 
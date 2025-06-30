#!/usr/bin/env python3
"""
Main demonstration script for the Python vitrea-client library.

This script shows how to use the vitrea-client to connect to a Vitrea vBox
and perform various operations like getting system information and controlling keys.
"""

import asyncio
import sys
from dotenv import load_dotenv
from vitrea_client import VitreaClient
from vitrea_client.core.logger import ConsoleLogger
from vitrea_client.exceptions import ConnectionExistsException, NoConnectionException, TimeoutException

# Load environment variables from .env file
load_dotenv()


async def main():
    """Main demonstration function."""
    print("🏠 Vitrea Client Python Demo")
    print("=" * 40)
    
    # Create client with console logging enabled
    client = VitreaClient.create(
        socket_config={'logger': ConsoleLogger()}
    )
    
    try:
        print(f"📡 Connecting to {client.connection_config.host}:{client.connection_config.port}")
        print(f"👤 Username: {client.connection_config.username or 'None'}")
        print(f"🔧 Protocol: {client.connection_config.version.value}")
        print()
        
        # Connect to the vBox
        await client.connect()
        print("✅ Connected successfully!")
        print()
        
        # Get system information
        print("📊 Getting system information...")
        room_count = 0
        node_count = 0
        try:
            room_count = await client.get_room_count()
            print(f"🏠 Room count: {room_count}")
            
            node_count = await client.get_node_count()
            print(f"🔌 Node count: {node_count}")
            print()
        except TimeoutException as e:
            print(f"⏰ Timeout getting system info: {e}")
        except Exception as e:
            print(f"❌ Error getting system info: {e}")
        
        # Try to get metadata for first room and node
        print("📋 Getting metadata...")
        try:
            if room_count > 0:
                room_metadata = await client.get_room_metadata(room_id=1)
                print(f"🏠 Room 1 name: {room_metadata.name}")
            
            if node_count > 0:
                node_metadata = await client.get_node_metadata(node_id=1)
                print(f"🔌 Node 1 MAC: {node_metadata.mac_address}")
                print(f"🔌 Node 1 keys: {len(node_metadata.keys)}")
                print()
        except Exception as e:
            print(f"⚠️  Could not get metadata: {e}")
            print()
        
        # Try to get key status (if nodes exist)
        if node_count > 0:
            print("🔑 Getting key status...")
            try:
                key_status = await client.get_key_status(node_id=1, key_id=1)
                print(f"🔑 Key 1-1 status: {'ON' if key_status.is_on else 'OFF'}")
                print(f"🔑 Key 1-1 released: {key_status.is_released}")
                print()
            except Exception as e:
                print(f"⚠️  Could not get key status: {e}")
                print()
        
        # Send a heartbeat
        print("💓 Sending heartbeat...")
        try:
            await client.send_heartbeat()
            print("✅ Heartbeat sent successfully!")
            print()
        except Exception as e:
            print(f"❌ Heartbeat failed: {e}")
            print()
        
        # Set up key status callback
        def on_key_status_update(status):
            print(f"🔔 Key status update: Node {status.node_id}, Key {status.key_id} -> {'ON' if status.is_on else 'OFF'}")
        
        client.on_key_status(on_key_status_update)
        print("👂 Listening for key status updates...")
        print("   (Press Ctrl+C to stop)")
        
        # Wait for status updates (or timeout after 10 seconds)
        try:
            await asyncio.sleep(10)
        except KeyboardInterrupt:
            print("\n⏹️  Stopped by user")
        
    except ConnectionExistsException:
        print("❌ Connection already exists!")
    except NoConnectionException:
        print("❌ No connection available!")
    except TimeoutException as e:
        print(f"⏰ Connection timeout: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"   Error type: {type(e).__name__}")
    finally:
        # Always disconnect
        try:
            await client.disconnect()
            print("🔌 Disconnected from vBox")
        except Exception as e:
            print(f"⚠️  Error during disconnect: {e}")


if __name__ == "__main__":
    print("Python Vitrea Client - Port of https://github.com/bdsoha/vitrea-client")
    print("Original TypeScript library by bdsoha")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1) 
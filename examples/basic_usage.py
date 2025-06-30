#!/usr/bin/env python3
"""Basic usage example for VitreaClient."""

import asyncio
import logging
from vitrea_client import VitreaClient
from vitrea_client.utilities import KeyPowerStatus


async def main():
    """Demonstrate basic VitreaClient usage."""
    
    # Set up logging to see what's happening
    logging.basicConfig(level=logging.INFO)
    
    # Create client with configuration
    # These values can also be set via environment variables:
    # VITREA_VBOX_HOST, VITREA_VBOX_PORT, VITREA_VBOX_USERNAME, VITREA_VBOX_PASSWORD
    client = VitreaClient.create({
        "connection_config": {
            "host": "192.168.1.23",  # Default Vitrea vBox IP
            "port": 11501,           # Default Vitrea vBox port
            "username": "admin",     # Your vBox username
            "password": "admin",     # Your vBox password
            "version": "v2"          # Protocol version (v1 or v2)
        },
        "socket_config": {
            "request_timeout": 10.0,    # Request timeout in seconds
            "request_buffer": 0.25,     # Buffer delay between requests
            "should_reconnect": True,   # Auto-reconnect on disconnect
            "ignore_ack_logs": True     # Don't log acknowledgement responses
        }
    })
    
    # Set up a key status listener to receive unsolicited updates
    def on_key_status_update(status):
        print(f"Key status update: Node {status.node_id}, Key {status.key_id}, Power: {status.power}")
        if status.is_on:
            print("  -> Key is ON")
        elif status.is_off:
            print("  -> Key is OFF")
        elif status.is_released:
            print("  -> Key is RELEASED")
    
    client.on_key_status(on_key_status_update)
    
    try:
        # Connect to the vBox
        print("Connecting to Vitrea vBox...")
        await client.connect()
        print("Connected successfully!")
        
        # Get system information
        print("\n=== System Information ===")
        room_count = await client.get_room_count()
        print(f"Number of rooms: {room_count}")
        
        node_count = await client.get_node_count()
        print(f"Number of nodes: {node_count}")
        
        # Get information about the first room (if it exists)
        if room_count > 0:
            print(f"\n=== Room 0 Information ===")
            room_metadata = await client.get_room_metadata(0)
            print(f"Room name: {room_metadata.room_name}")
        
        # Get information about the first node (if it exists)
        if node_count > 0:
            print(f"\n=== Node 0 Information ===")
            node_metadata = await client.get_node_metadata(0)
            print(f"Node ID: {node_metadata.id}")
            print(f"MAC Address: {node_metadata.mac_address}")
            print(f"Version: {node_metadata.version}")
            print(f"Total Keys: {node_metadata.total_keys}")
            print(f"Lock Status: {'Locked' if node_metadata.lock_status == 1 else 'Unlocked'}")
            print(f"LED Level: {node_metadata.led_level}")
            
            # List all keys for this node
            print("Keys:")
            for key_info in node_metadata.keys_list:
                print(f"  Key {key_info['id']}: Type {key_info['type']}")
            
            # Get status of the first key (if it exists)
            if node_metadata.total_keys > 0:
                print(f"\n=== Key 0 Status ===")
                key_status = await client.get_key_status(0, 0)
                print(f"Key Status - Node: {key_status.node_id}, Key: {key_status.key_id}")
                print(f"Power Status: {key_status.power}")
                print(f"Is On: {key_status.is_on}")
                print(f"Is Off: {key_status.is_off}")
                
                # Get key parameters
                key_params = await client.get_key_parameters(0, 0)
                print(f"Key Category: {key_params.category}")
                print(f"Dimmer Ratio: {key_params.dimmer_ratio}")
        
        # Example: Control a key (uncomment to test)
        # WARNING: This will actually control your lights!
        """
        print(f"\n=== Key Control Example ===")
        print("Turning key ON...")
        await client.turn_key_on(0, 0, dimmer_ratio=50)  # 50% brightness
        
        await asyncio.sleep(2)  # Wait 2 seconds
        
        print("Turning key OFF...")
        await client.turn_key_off(0, 0)
        """
        
        # Send a manual heartbeat
        print(f"\n=== Manual Heartbeat ===")
        await client.send_heartbeat()
        print("Heartbeat sent successfully")
        
        # Wait a bit to receive any status updates
        print(f"\nWaiting 5 seconds for status updates...")
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Disconnect
        print("\nDisconnecting...")
        client.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    asyncio.run(main()) 
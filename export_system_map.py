#!/usr/bin/env python3
"""
Export Vitrea system mapping to JSON file.

This script connects to the Vitrea vBox and exports all rooms, nodes, and switches
to a JSON file for system documentation and mapping purposes.
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

from vitrea_client import VitreaClient
from vitrea_client.core.logger import ConsoleLogger
from vitrea_client.exceptions import ConnectionExistsException, NoConnectionException, TimeoutException

# Load environment variables from .env file
load_dotenv()


async def export_system_map():
    """Export complete system mapping to JSON."""
    print("🏠 Vitrea System Mapping Export")
    print("=" * 50)
    
    # Create client with console logging
    client = VitreaClient.create(
        socket_config={'logger': ConsoleLogger()}
    )
    
    system_map = {
        "export_info": {
            "timestamp": datetime.now().isoformat(),
            "exported_by": "Python vitrea-client",
            "original_library": "https://github.com/bdsoha/vitrea-client"
        },
        "connection": {
            "host": client.connection_config.host,
            "port": client.connection_config.port,
            "protocol_version": client.connection_config.version.value
        },
        "rooms": [],
        "nodes": [],
        "room_node_mapping": {},
        "summary": {}
    }
    
    try:
        print(f"📡 Connecting to {client.connection_config.host}:{client.connection_config.port}")
        await client.connect()
        print("✅ Connected successfully!")
        print()
        
        # Get system counts
        print("📊 Getting system overview...")
        room_count = await client.get_room_count()
        node_count = await client.get_node_count()
        
        print(f"🏠 Total rooms: {room_count}")
        print(f"🔌 Total nodes: {node_count}")
        print()
        
        system_map["summary"] = {
            "total_rooms": room_count,
            "total_nodes": node_count,
            "total_keys": 0  # Will be calculated
        }
        
        # Get all room information
        print("🏠 Exporting room information...")
        rooms_data = []
        
        # Get the actual room list first
        from vitrea_client.requests import RoomCount
        room_count_response = await client.send(RoomCount())
        room_ids = room_count_response.list  # This gives us the actual room IDs
        
        for room_id in room_ids:
            try:
                print(f"  📋 Getting room {room_id} metadata...")
                room_metadata = await client.get_room_metadata(room_id)
                
                room_info = {
                    "room_id": room_id,
                    "name": room_metadata.name,
                    "raw_name_data": bytes(room_metadata.data).hex() if hasattr(room_metadata, 'data') and room_metadata.data else None
                }
                
                rooms_data.append(room_info)
                print(f"    ✅ Room {room_id}: '{room_metadata.name}'")
                
            except Exception as e:
                print(f"    ❌ Failed to get room {room_id}: {e}")
                rooms_data.append({
                    "room_id": room_id,
                    "name": f"Room {room_id} (Error)",
                    "error": str(e)
                })
        
        system_map["rooms"] = rooms_data
        print(f"✅ Exported {len(rooms_data)} rooms")
        print()
        
        # Get all node information
        print("🔌 Exporting node information...")
        nodes_data = []
        total_keys = 0
        
        # First get the list of actual node IDs
        from vitrea_client.requests import NodeCount
        node_count_response = await client.send(NodeCount())
        node_ids = node_count_response.list  # This gives us the actual node IDs
        
        for node_id in node_ids:
            try:
                print(f"  📋 Getting node {node_id} metadata...")
                node_metadata = await client.get_node_metadata(node_id)
                
                # Handle both V1 and V2 responses
                node_info = {
                    "node_id": node_id,
                    "mac_address": getattr(node_metadata, 'mac_address', 'Unknown'),
                    "version": getattr(node_metadata, 'version', 'Unknown'),
                    "keys": [],
                    "total_keys": 0,
                    "lock_status": getattr(node_metadata, 'lock_status', None),
                    "led_level": getattr(node_metadata, 'led_level', None)
                }
                
                # Get keys list
                if hasattr(node_metadata, 'keys'):
                    node_info["keys"] = node_metadata.keys
                    node_info["total_keys"] = len(node_metadata.keys)
                    total_keys += len(node_metadata.keys)
                
                # Get key details for each key
                key_details = []
                if node_info["keys"]:
                    print(f"    🔑 Getting details for {len(node_info['keys'])} keys...")
                    
                    for key_id in node_info["keys"]:
                        try:
                            # Get key status
                            key_status = await client.get_key_status(node_id, key_id)
                            
                            # Get key parameters
                            try:
                                key_params = await client.get_key_parameters(node_id, key_id)
                                key_detail = {
                                    "key_id": key_id,
                                    "name": getattr(key_params, 'name', ''),
                                    "status": {
                                        "power": key_status.power.name,
                                        "is_on": key_status.is_on,
                                        "is_off": key_status.is_off,
                                        "is_released": key_status.is_released
                                    },
                                    "parameters": {
                                        "category": getattr(key_params, 'category', 'Unknown'),
                                        "dimmer_ratio": getattr(key_params, 'dimmer_ratio', 0)
                                    }
                                }
                            except Exception as e:
                                key_detail = {
                                    "key_id": key_id,
                                    "status": {
                                        "power": key_status.power.name,
                                        "is_on": key_status.is_on,
                                        "is_off": key_status.is_off,
                                        "is_released": key_status.is_released
                                    },
                                    "parameters": {"error": str(e)}
                                }
                            
                            key_details.append(key_detail)
                            key_name = getattr(key_params, 'name', '') if 'key_params' in locals() else ''
                            name_display = f" '{key_name}'" if key_name else ""
                            print(f"      ✅ Key {key_id}{name_display}: {key_status.power.name}")
                            
                        except Exception as e:
                            print(f"      ❌ Failed to get key {key_id} details: {e}")
                            key_details.append({
                                "key_id": key_id,
                                "error": str(e)
                            })
                
                node_info["key_details"] = key_details
                nodes_data.append(node_info)
                print(f"    ✅ Node {node_id}: {node_info['total_keys']} keys")
                
            except Exception as e:
                print(f"    ❌ Failed to get node {node_id}: {e}")
                nodes_data.append({
                    "node_id": node_id,
                    "error": str(e)
                })
        
        system_map["nodes"] = nodes_data
        system_map["summary"]["total_keys"] = total_keys
        print(f"✅ Exported {len(nodes_data)} nodes with {total_keys} total keys")
        print()
        
        # Create room-node mapping (this would need additional logic based on your system)
        print("🔗 Creating room-node mapping...")
        # For now, we'll create a placeholder mapping
        # In a real system, you'd need additional API calls or configuration to map nodes to rooms
        system_map["room_node_mapping"] = {
            "note": "Room-node mapping requires additional system knowledge or configuration",
            "rooms": {str(room["room_id"]): {"name": room["name"], "nodes": []} for room in rooms_data}
        }
        
        print("✅ System mapping complete!")
        print()
        
    except ConnectionExistsException:
        print("❌ Connection already exists!")
        return None
    except NoConnectionException:
        print("❌ No connection available!")
        return None
    except TimeoutException as e:
        print(f"⏰ Connection timeout: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None
    finally:
        try:
            await client.disconnect()
            print("🔌 Disconnected from vBox")
        except Exception as e:
            print(f"⚠️  Error during disconnect: {e}")
    
    return system_map


async def main():
    """Main function to export system map and save to JSON."""
    print("Python Vitrea Client - System Mapping Export")
    print("Original TypeScript library by bdsoha: https://github.com/bdsoha/vitrea-client")
    print()
    
    try:
        system_map = await export_system_map()
        
        if system_map:
            # Save to JSON file
            filename = f"vitrea_system_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            print(f"💾 Saving system map to {filename}...")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(system_map, f, indent=2, ensure_ascii=False)
            
            print(f"✅ System map saved successfully!")
            print()
            print("📊 Summary:")
            print(f"  🏠 Rooms: {system_map['summary']['total_rooms']}")
            print(f"  🔌 Nodes: {system_map['summary']['total_nodes']}")
            print(f"  🔑 Keys: {system_map['summary']['total_keys']}")
            print(f"  📄 File: {filename}")
            
        else:
            print("❌ Failed to export system map")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Export cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 
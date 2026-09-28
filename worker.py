# ============================================
# FILE: worker.py (PERSISTENT CONNECTION - FIXED)
# CHANGES:
# 1. Connection stays alive for MULTIPLE chunks
# 2. No reconnection after each chunk
# 3. Continuous task processing until master closes connection
# 4. Better error handling
# ============================================

import socket
import json
import pandas as pd
import time
import psutil
import io
import zlib
import struct

# ============================================
# CONFIGURATION - CHANGE THIS TO YOUR MASTER IP
# ============================================
MASTER_IP = '192.168.100.15'  # Master laptop ki IP dalo
MASTER_PORT = 5000

def get_system_usage():
    """Get current system metrics"""
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
    }

def print_status(msg, symbol="✓"):
    print(f"{symbol} {msg}")

def start_worker():
    print("\n" + "="*50)
    print("DCDAS WORKER NODE")
    print("="*50)
    print(f"Looking for master at: {MASTER_IP}:{MASTER_PORT}")
    
    while True:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((MASTER_IP, MASTER_PORT))
            print_status("Connected to master! Waiting for tasks...", "🔌")
            
            # CONTINUOUS LOOP - Same connection pe multiple tasks
            while True:
                # Receive header (8 bytes = payload size)
                header = client_socket.recv(8)
                if not header:
                    print("Master closed connection. Reconnecting...")
                    break
                
                payload_size = struct.unpack("Q", header)[0]
                print(f"Receiving {payload_size/1024/1024:.2f} MB of data...")
                
                # Receive compressed data
                compressed_data = b""
                while len(compressed_data) < payload_size:
                    chunk = client_socket.recv(1024 * 1024)
                    if not chunk:
                        break
                    compressed_data += chunk
                
                # Decompress
                raw_json = zlib.decompress(compressed_data).decode('utf-8')
                task = json.loads(raw_json)
                
                chunk_id = task['chunk_id']
                start_time = time.time()
                print(f"⚡ Processing Chunk-{chunk_id}...")
                
                # Convert to DataFrame
                full_df = pd.read_json(io.StringIO(task['data']))
                
                # Compute analytics
                crime_col = 'Crime type' if 'Crime type' in full_df.columns else full_df.columns[0]
                month_col = 'Month_Name' if 'Month_Name' in full_df.columns else 'Month'
                
                crime_types = full_df[crime_col].value_counts().to_dict()
                monthly_trends = full_df[month_col].value_counts().to_dict()
                
                outcomes = {}
                if 'Last outcome category' in full_df.columns:
                    outcomes = full_df['Last outcome category'].fillna("Unknown").value_counts().to_dict()
                
                process_time = round(time.time() - start_time, 2)
                usage = get_system_usage()
                
                # Build result
                result = {
                    "chunk_id": chunk_id,
                    "total_crimes": len(full_df),
                    "crime_types": crime_types,
                    "monthly_trends": monthly_trends,
                    "outcomes": outcomes,
                    "system_health": {
                        "cpu": usage['cpu'],
                        "ram": usage['ram'],
                    }
                }
                
                # Send results back
                final_payload = (json.dumps(result) + "---FINAL---").encode('utf-8')
                client_socket.sendall(final_payload)
                print_status(f"Chunk-{chunk_id} done in {process_time}s", "✅")
                
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
            print(f"❌ Connection lost: {e}. Reconnecting in 3 seconds...")
            time.sleep(3)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(3)
        finally:
            try:
                client_socket.close()
            except:
                pass

if __name__ == "__main__":
    start_worker()
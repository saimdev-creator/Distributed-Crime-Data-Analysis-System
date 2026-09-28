import socket
import json
import threading
import psutil
import os
import struct # Added for reliable data transfer
import pandas as pd

# Global storage remains exactly as yours
final_results = {
    "total_crimes": 0,
    "crime_types": {},
    "monthly_trends": {},
    "top_areas": {}, 
    "outcomes": {},   
    "map_coords": [],
    "worker_stats": [], 
    "live_status": {}, 
    "master_system": {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent
    },
    "workers_completed": 0
}

DATASET_PATH = 'datasets/processed/CRIME_DATA_CLEANED.csv' 
data_lock = threading.Lock()

def merge_results(worker_data):
    global final_results
    with data_lock:
        final_results["total_crimes"] += worker_data.get("total_crimes", 0)
        # Dictionary merging
        for key in ["crime_types", "monthly_trends"]:
            for item, count in worker_data.get(key, {}).items():
                final_results[key][item] = final_results[key].get(item, 0) + count
        
        # Area and Outcomes logic kept same
        for area, count in worker_data.get("crime_types", {}).items(): 
            final_results["top_areas"][area] = final_results["top_areas"].get(area, 0) + count
        
        final_results["worker_stats"].append(worker_data.get("system_health", {}))
        final_results["workers_completed"] += 1

def process_locally_on_master(df_chunk, worker_id):
    """Fallback: Agar worker fail ho jaye toh Master khud calculate karega"""
    print(f"⚙️ Fallback: Master is processing data for Worker-{worker_id}...")
    local_res = {
        "total_crimes": len(df_chunk),
        "crime_types": df_chunk['Crime type'].value_counts().to_dict(),
        "monthly_trends": df_chunk['Month'].value_counts().to_dict(),
        "system_health": {"id": f"Master-Backup-{worker_id}", "cpu": 0, "ram": 0}
    }
    merge_results(local_res)
    final_results["live_status"][f"Worker-{worker_id}"] = {"status": "Self-Processed", "progress": 100}

def handle_worker(conn, addr, worker_id, data_chunk):
    global final_results
    print(f"✅ Worker-{worker_id} connected from {addr}")
    
    try:
        # 1. Prepare Payload
        task_json = json.dumps({
            "worker_id": worker_id, 
            "data": data_chunk.to_json(orient='records')
        }).encode('utf-8')
        
        # 2. Send Size Header (Fixed 8 bytes)
        payload_size = len(task_json)
        conn.sendall(struct.pack("Q", payload_size)) 
        
        # 3. Stream Data in Chunks (Prevents WinError 10054)
        print(f"📦 Sending {payload_size/1024/1024:.2f} MB to Worker-{worker_id}...")
        conn.sendall(task_json)
        
        # 4. Receiving Results
        conn.settimeout(180.0) 
        raw_res = b""
        while True:
            chunk = conn.recv(1024*1024) 
            if not chunk: break
            raw_res += chunk
            if b"---FINAL---" in raw_res:
                break
        
        if raw_res:
            clean_data = raw_res.replace(b"---FINAL---", b"").decode('utf-8')
            worker_res = json.loads(clean_data)
            merge_results(worker_res)
            final_results["live_status"][f"Worker-{worker_id}"] = {"status": "Completed", "progress": 100}
            print(f"📩 Worker-{worker_id} Results Merged Successfully.")
            
    except (ConnectionResetError, socket.timeout, Exception) as e:
        print(f"⚠️ FAULT: Worker-{worker_id} Error: {e}. Switching to Master processing...")
        process_locally_on_master(data_chunk, worker_id)
    finally:
        conn.close()

def save_current_state():
    if not os.path.exists('outputs'): os.makedirs('outputs')
    with open('outputs/dashboard_data.json', 'w') as f:
        json.dump(final_results, f, indent=4)

def load_and_partition(n):
    print(f"📖 Loading dataset: {DATASET_PATH}")
    if not os.path.exists(DATASET_PATH):
        return []
    df = pd.read_csv(DATASET_PATH)
    avg = len(df) // n
    return [df[i*avg:(i+1)*avg] for i in range(n)]

def start_master():
    num_workers = 1 # Change this based on your available laptops
    chunks = load_and_partition(num_workers) 

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Using 0.0.0.0 to listen on all interfaces
    server_socket.bind(('0.0.0.0', 5000)) 
    server_socket.listen(num_workers)
    
    print(f"🚀 MASTER LIVE on Port 5000")
    print(f"📡 Waiting for {num_workers} Worker(s)...")
    
    threads = []
    for i in range(1, num_workers + 1): 
        final_results["live_status"][f"Worker-{i}"] = {"status": "Waiting", "progress": 0}
        conn, addr = server_socket.accept()
        t = threading.Thread(target=handle_worker, args=(conn, addr, i, chunks[i-1]))
        t.start()
        threads.append(t)
    
    for t in threads: t.join() 
    save_current_state()
    print("\n🔥 BATCH COMPLETE. Results in outputs/dashboard_data.json")

if __name__ == "__main__":
    start_master()
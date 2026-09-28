# ============================================
# FILE: master.py (FINAL - WORKING VERSION)
# TIMEOUT: 30 seconds for 3 workers
# LOAD BALANCING: Master + Workers
# ============================================

import socket
import json
import threading
import psutil
import os
import struct 
import pandas as pd
import zlib
import time
from queue import Queue

CHUNKS_DIR = 'datasets/processed/chunks/'
OUTPUT_FILE = 'outputs/dashboard_data.json'

# Track fault events
fault_events = []
scheduling_log = []

# Thread-safe global layout
final_results = {
    "total_crimes": 0,
    "crime_types": {},
    "monthly_trends": {},
    "top_areas": {}, 
    "outcomes": {},   
    "worker_stats": {},
    "live_status": {
        "Master-Node": {"status": "Standby", "progress": 100},
        "Worker-Node": {"status": "Waiting for workers", "progress": 0}
    }, 
    "master_system": {"cpu": 0, "ram": 0},
    "chunks_completed": 0,
    "pipeline_state": "standby",
    "fault_events_count": 0,
    "scheduling_info": []
}

data_lock = threading.Lock()
task_queue = Queue()
active_workers = {}

def print_banner(text):
    print(f"\n{'='*60}\n{text:^60}\n{'='*60}")

def merge_results(worker_data, worker_id, chunk_id, processing_time):
    """Thread-safe aggregation of chunk results"""
    global final_results
    with data_lock:
        final_results["total_crimes"] += worker_data.get("total_crimes", 0)
        
        for key in ["crime_types", "monthly_trends", "outcomes"]:
            for item, count in worker_data.get(key, {}).items():
                if pd.isna(item) or item == "" or str(item).strip().lower() == "nan":
                    item = "Unknown"
                final_results[key][item] = final_results[key].get(item, 0) + count
        
        for area, count in worker_data.get("crime_types", {}).items(): 
            final_results["top_areas"][area] = final_results["top_areas"].get(area, 0) + count
        
        if "system_health" in worker_data:
            h = worker_data["system_health"]
            final_results["worker_stats"][worker_id] = {
                "id": worker_id,
                "cpu": h.get("cpu", 0),
                "ram": h.get("ram", 0),
                "last_processed_chunk": chunk_id,
                "processing_time": processing_time,
                "status": "DONE"
            }
        
        final_results["chunks_completed"] += 1
        progress = int((final_results["chunks_completed"] / 10) * 100)
        final_results["live_status"]["Worker-Node"]["progress"] = progress
        save_current_state()

def save_current_state():
    """Save state to JSON"""
    final_results["master_system"]["cpu"] = psutil.cpu_percent()
    final_results["master_system"]["ram"] = psutil.virtual_memory().percent
    if not os.path.exists('outputs'): 
        os.makedirs('outputs')
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(final_results, f, indent=4)

def process_locally_on_master(chunk_file, chunk_id):
    """Master processes a chunk locally (used for load balancing & fault tolerance)"""
    start_time = time.time()
    print(f"⚙️ Master processing Chunk-{chunk_id} locally...")
    
    try:
        df_chunk = pd.read_csv(os.path.join(CHUNKS_DIR, chunk_file))
        crime_col = 'Crime type' if 'Crime type' in df_chunk.columns else df_chunk.columns[0]
        month_col = 'Month' if 'Month' in df_chunk.columns else df_chunk.columns[1]
        outcome_col = 'Last outcome category' if 'Last outcome category' in df_chunk.columns else None

        local_res = {
            "total_crimes": len(df_chunk),
            "crime_types": df_chunk[crime_col].value_counts().to_dict(),
            "monthly_trends": df_chunk[month_col].value_counts().to_dict(),
            "outcomes": df_chunk[outcome_col].value_counts().to_dict() if outcome_col else {},
            "system_health": {"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent}
        }
        
        processing_time = round(time.time() - start_time, 2)
        merge_results(local_res, "Master-Local", chunk_id, processing_time)
        
        # Log scheduling
        scheduling_log.append({"chunk": chunk_id, "worker": "Master-Local", "time": processing_time})
        with data_lock:
            final_results["scheduling_info"] = scheduling_log[-10:]
        
        print(f"✓ Master completed Chunk-{chunk_id} in {processing_time}s")
        return True
    except Exception as e:
        print(f"❌ Master failed on Chunk-{chunk_id}: {e}")
        return False

def worker_thread_handler(conn, addr):
    """Handle worker connection and assign tasks"""
    worker_id = f"Worker-{addr[0]}"
    print(f"✅ Worker connected: {worker_id}")
    
    with data_lock:
        final_results["worker_stats"][worker_id] = {
            "id": worker_id, "cpu": 0, "ram": 0, "last_processed_chunk": "None", 
            "status": "CONNECTED", "processing_time": 0
        }
        save_current_state()

    try:
        while True:
            try:
                chunk_file, chunk_id = task_queue.get_nowait()
            except Exception:
                # No more chunks in queue - worker can exit
                break
            
            try:
                start_time = time.time()
                print(f"📡 Assigning Chunk-{chunk_id} → {worker_id}")
                
                scheduling_log.append({"chunk": chunk_id, "worker": worker_id, "start_time": time.time()})
                
                df = pd.read_csv(os.path.join(CHUNKS_DIR, chunk_file))
                task_json = json.dumps({"chunk_id": chunk_id, "data": df.to_json(orient='records')}).encode('utf-8')
                
                compressed_payload = zlib.compress(task_json)
                payload_size = len(compressed_payload)
                
                conn.sendall(struct.pack("Q", payload_size)) 
                conn.sendall(compressed_payload)
                
                with data_lock:
                    final_results["worker_stats"][worker_id]["status"] = f"PROCESSING {chunk_id}"
                    save_current_state()

                conn.settimeout(120.0) 
                raw_res = b""
                while True:
                    packet = conn.recv(1024*1024) 
                    if not packet: break
                    raw_res += packet
                    if b"---FINAL---" in raw_res: break
                
                if raw_res:
                    processing_time = round(time.time() - start_time, 2)
                    clean_data = raw_res.replace(b"---FINAL---", b"").decode('utf-8')
                    merge_results(json.loads(clean_data), worker_id, chunk_id, processing_time)
                    
                    for log in scheduling_log:
                        if log["chunk"] == chunk_id and log["worker"] == worker_id:
                            log["time"] = processing_time
                    with data_lock:
                        final_results["scheduling_info"] = scheduling_log[-10:]
                    
                    print(f"✅ {worker_id} completed Chunk-{chunk_id} in {processing_time}s")
                    task_queue.task_done()
                    
            except Exception as e:
                print(f"⚠️ Worker {worker_id} failed on Chunk-{chunk_id}: {e}")
                # Re-queue the chunk for another worker or master
                task_queue.put((chunk_file, chunk_id))
                task_queue.task_done()
                
                fault_events.append({"chunk": chunk_id, "time": time.time(), "reason": str(e)})
                with data_lock:
                    final_results["fault_events_count"] = len(fault_events)
                break
                
    except Exception as e:
        print(f"Error with {worker_id}: {e}")
    finally:
        with data_lock:
            final_results["worker_stats"][worker_id]["status"] = "DISCONNECTED"
            save_current_state()
        conn.close()

def start_master():
    # Reset old dashboard data
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print("🗑️ Old dashboard data cleared. Fresh run starting...")
    
    if not os.path.exists(CHUNKS_DIR):
        print(f"❌ Error: {CHUNKS_DIR} not found! Run partitioner.py first.")
        return
    
    chunk_files = sorted([f for f in os.listdir(CHUNKS_DIR) if f.startswith('chunk_') and f.endswith('.csv')])
    if not chunk_files:
        print("❌ Error: No chunk files found!")
        return

    for f in chunk_files:
        cid = f.split('_')[1].split('.')[0]
        task_queue.put((f, cid))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 5000)) 
    server_socket.listen(5)
    
    print_banner("DCDAS MASTER NODE")
    print(f"📦 Total chunks: {len(chunk_files)}")
    print("⏳ Waiting for workers (30s timeout)...")
    
    final_results["live_status"]["Master-Node"]["status"] = "Waiting for workers"
    final_results["pipeline_state"] = "processing"
    save_current_state()

    server_socket.settimeout(30.0)  # 30 seconds for 3 workers
    threads = []
    start_time = time.time()

    # Accept worker connections
    while time.time() - start_time < 30.0:
        if task_queue.empty():
            break
        try:
            conn, addr = server_socket.accept()
            t = threading.Thread(target=worker_thread_handler, args=(conn, addr), daemon=True)
            t.start()
            threads.append(t)
            print(f"✅ Worker {addr[0]} connected and ready")
        except socket.timeout:
            if len(final_results["worker_stats"]) > 0:
                print(f"\n⏰ Timeout reached. {len(final_results['worker_stats'])} worker(s) connected. Continuing...")
                break
            else:
                print("\n⏰ No workers connected. Master will process all chunks locally.")
                final_results["live_status"]["Worker-Node"]["status"] = "Offline - Master processing"
                save_current_state()
                break

        # ============================================================
    # LOAD BALANCING: Master also processes chunks alongside workers
    # ============================================================
    print("\n" + "="*50)
    print("LOAD BALANCING ACTIVE: Master + Workers processing chunks")
    print("="*50)
    
    master_chunks_processed = 0
    max_master_chunks = 3  # Master will process at most 3 chunks
    
    while not task_queue.empty():
        # Check if any worker threads are still alive
        active_workers = any(t.is_alive() for t in threads)
        
        if not active_workers:
            # No workers left - master processes all remaining chunks
            print("\n📡 No active workers. Master processing all remaining chunks...")
            while not task_queue.empty():
                try:
                    cf, cid = task_queue.get_nowait()
                    process_locally_on_master(cf, cid)
                    task_queue.task_done()
                except Exception:
                    break
            break
        
        # Workers are active - master also takes some chunks (load balancing)
        if master_chunks_processed < max_master_chunks:
            try:
                cf, cid = task_queue.get_nowait()
                process_locally_on_master(cf, cid)
                task_queue.task_done()
                master_chunks_processed += 1
                print(f"📊 Load balance: Master took Chunk-{cid} ({master_chunks_processed}/{max_master_chunks})")
            except Exception:
                pass
        
        # Small delay to let workers process
        time.sleep(0.5)
    
    # Wait for all worker threads to finish
    print("\n⏳ Waiting for workers to complete remaining chunks...")
    for t in threads:
        t.join(timeout=30.0)
    
    # Final check - if any chunks left, master processes them
    while not task_queue.empty():
        try:
            cf, cid = task_queue.get_nowait()
            print(f"📡 Final fallback: Master processing Chunk-{cid}")
            process_locally_on_master(cf, cid)
            task_queue.task_done()
        except Exception:
            break

    final_results["live_status"]["Master-Node"]["status"] = "Done"
    final_results["pipeline_state"] = "completed"
    save_current_state()
    
    print_banner("PROCESSING / Batch COMPLETE")
    print(f"📊 Summary: {final_results['chunks_completed']}/10 chunks processed")
    print(f"   - Master processed: {master_chunks_processed} chunks")
    print(f"   - Workers processed: {final_results['chunks_completed'] - master_chunks_processed} chunks")

if __name__ == "__main__":
    start_master()
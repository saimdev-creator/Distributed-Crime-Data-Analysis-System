# ============================================
# FILE: partitioner.py (PATH FIXED VERSION)
# PURPOSE: Split transformed data into balanced chunks
# ============================================

import pandas as pd
import os
import numpy as np
import json

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # DCDAS folder

INPUT_PATH = os.path.join(BASE_DIR, "datasets", "processed", "CRIME_DATA_TRANSFORMED.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "datasets", "processed", "chunks")

def split_dataset(num_chunks=10):
    try:
        # 1. Create directory
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            print(f"📁 Created directory: {OUTPUT_DIR}")

        # 2. Check if file exists
        if not os.path.exists(INPUT_PATH):
            print(f"❌ Error: {INPUT_PATH} not found!")
            print("   Run transform.py first!")
            return

        # 3. Load Transformed Data
        print(f"📖 Loading: {INPUT_PATH}")
        df = pd.read_csv(INPUT_PATH)
        total_rows = len(df)
        
        print(f"📊 Dataset Info:")
        print(f"   - Total Rows: {total_rows:,}")
        print(f"   - Columns: {len(df.columns)}")
        
        # 4. Shuffle Data for balanced distribution
        print("\n🔀 Shuffling data for balanced distribution...")
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)

        # 5. Split into Chunks
        print(f"\n✂️  Splitting into {num_chunks} chunks...\n")

        chunk_size = int(np.ceil(total_rows / num_chunks))
        
        chunk_stats = []

        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, total_rows)
            
            if start_idx >= total_rows:
                break
                
            chunk_df = df.iloc[start_idx:end_idx]
            
            chunk_filename = os.path.join(OUTPUT_DIR, f"chunk_{i+1}.csv")
            chunk_df.to_csv(chunk_filename, index=False)
            
            stats = {
                'chunk': i+1,
                'rows': len(chunk_df)
            }
            chunk_stats.append(stats)
            
            print(f"✅ chunk_{i+1}.csv → {len(chunk_df):,} rows")

        # 6. Save metadata
        metadata_path = os.path.join(OUTPUT_DIR, 'chunks_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(chunk_stats, f, indent=4)

        print(f"\n{'='*50}")
        print("🔥 PARTITIONING COMPLETE!")
        print(f"{'='*50}")
        print(f"📁 Location: {OUTPUT_DIR}")
        print(f"📦 Total Chunks: {len(chunk_stats)}")
        print(f"📊 Total Rows: {total_rows:,}")
        print(f"📋 Metadata saved to: {metadata_path}")

    except Exception as e:
        print(f"❌ Partitioning failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    split_dataset(10)
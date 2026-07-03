import os
import shutil

def select_best():
    dense_dir = "dataset/dsl"
    sparse_dir = "dataset/dsl_sparse"
    final_dir = "dataset/dsl_final"
    
    os.makedirs(final_dir, exist_ok=True)
    
    files = [f for f in os.listdir(dense_dir) if f.endswith('.txt')]
    
    count_dense = 0
    count_sparse = 0
    
    for f in files:
        dense_path = os.path.join(dense_dir, f)
        sparse_path = os.path.join(sparse_dir, f)
        final_path = os.path.join(final_dir, f)
        
        # Default to dense if sparse doesn't exist for some reason
        if not os.path.exists(sparse_path):
            shutil.copy2(dense_path, final_path)
            count_dense += 1
            continue
            
        dense_size = os.path.getsize(dense_path)
        sparse_size = os.path.getsize(sparse_path)
        
        if sparse_size <= dense_size:
            shutil.copy2(sparse_path, final_path)
            count_sparse += 1
        else:
            shutil.copy2(dense_path, final_path)
            count_dense += 1
            
    print(f"Comparison complete.")
    print(f"Selected Sparse: {count_sparse}")
    print(f"Selected Dense: {count_dense}")
    print(f"Total files in final: {len(os.listdir(final_dir))}")

if __name__ == "__main__":
    select_best()

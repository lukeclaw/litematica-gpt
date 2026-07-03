import os
import re

def sanitize_filename(name):
    # Remove characters that are generally invalid for filenames
    return re.sub(r'[\/*?:"<>|]', "", name).strip()

def rename_files(index_path, target_dir):
    if not os.path.exists(index_path):
        print(f"Index file not found: {index_path}")
        return

    with open(index_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    count = 0
    for line in lines:
        match = re.match(r'^(\d+)\s*-\s*(.*)$', line.strip())
        if match:
            file_id = match.group(1)
            description = match.group(2)
            
            old_name = f"{file_id}.txt"
            old_path = os.path.join(target_dir, old_name)
            
            if os.path.exists(old_path):
                new_name = sanitize_filename(f"{file_id} - {description}") + ".txt"
                new_path = os.path.join(target_dir, new_name)
                
                try:
                    os.rename(old_path, new_path)
                    count += 1
                except Exception as e:
                    print(f"Error renaming {old_name}: {e}")

    print(f"Successfully renamed {count} files.")

if __name__ == "__main__":
    index_file = "dataset/index.txt"
    dsl_dir = "dataset/dsl"
    rename_files(index_file, dsl_dir)

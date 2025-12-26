
import re

def check_missing_ids():
    path = 'c:/Users/User/Downloads/zip/index.tsx'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all "id": N
    ids = [int(m) for m in re.findall(r'"id":\s*(\d+)', content)]
    ids.sort()
    
    print(f"Total IDs found: {len(ids)}")
    if not ids:
        print("No IDs found!")
        return

    print(f"Range: {ids[0]} to {ids[-1]}")
    
    missing = []
    expected = 1
    for i in range(ids[0], ids[-1] + 1):
        if i not in ids:
            missing.append(i)
            
    if missing:
        print(f"Missing IDs: {missing}")
    else:
        print("No IDs missing in the range.")

check_missing_ids()

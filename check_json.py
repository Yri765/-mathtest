
import json

try:
    with open('c:/Users/User/Downloads/zip/questions.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    print(f"Total questions in JSON: {len(questions)}")
    
    # Check IDs
    ids = [q['id'] for q in questions]
    ids.sort()
    print(f"ID Range: {ids[0]} to {ids[-1]}")
    if len(ids) != len(set(ids)):
        print("Duplicates found in JSON IDs")
    else:
        print("No duplicates in JSON IDs")
            
except Exception as e:
    print(f"Error: {e}")

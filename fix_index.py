
import json
import re

def fix_index():
    index_path = 'c:/Users/User/Downloads/zip/index.tsx'
    json_path = 'c:/Users/User/Downloads/zip/questions_dump.json'

    # Read the JSON content as a raw string
    with open(json_path, 'r', encoding='utf-8') as f:
        # We want the exact text representation of the JSON, 
        # which effectively is valid JS object/array literal syntax too
        new_pool_content = f.read().strip()

    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the start and end of the QUESTION_POOL definition
    # We look for: const QUESTION_POOL: Question[] = [ ... ];
    # But since we messed it up, it might look slightly different or just match the previous pattern.
    
    start_marker = "const QUESTION_POOL: Question[] ="
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Could not find start marker")
        return

    # Find the next semicolon, assuming it ends the declaration. 
    # But the array content might contain semicolons in strings.
    # Be careful. We expect the declaration to end with `];` at the end of the array.
    # However, since we wrote it before, we can look for `];` followed by newline or next const.
    # A safer way relies on matching strict definition structure or just replacement.
    
    # We know the JSON starts with `[` and ends with `]`.
    # Let's see what's currently there.
    # It might be `const QUESTION_POOL: Question[] = [ ... ];`
    
    # Let's find the `[` after start_marker
    array_start_idx = content.find('[', start_idx)
    
    if array_start_idx == -1:
        print("Could not find array start")
        return
        
    # Now we need to find the matching closing bracket `]`.
    # Since we can't easily parse nested brackets without a parser, 
    # we can try to find `];` which is typical for the end of the statement in this file.
    
    # We will search for `];` occurring after array_start_idx.
    # Be aware that `];` could appear inside a string, though unlikely in this specific JSON.
    
    # A robust heuristic for this specific file:
    # The next declaration is `const SHUFFLE_COUNT = 30;`
    next_decl = "const SHUFFLE_COUNT"
    end_limit_idx = content.find(next_decl)
    
    if end_limit_idx == -1:
        # Fallback if next decl not found (maybe moved)
        # Search for `];`
        # But wait, looking at the large file view, QUESTION_POOL is huge.
        pass

    # Actually, simpler: Use regex to find the range, then replace by index slicing.
    # The regex from before worked to FIND it, just the substitution was broken.
    
    pattern = re.compile(r'(const QUESTION_POOL: Question\[\] = )(\[.*?\])(;)', re.DOTALL)
    match = pattern.search(content)
    
    if not match:
        print("Regex match failed")
        return
        
    # Construct new content using slicing to avoid re.sub escaping issues
    # match.start(2) is start of the array `[`
    # match.end(2) is end of the array `]`
    
    new_content = content[:match.start(2)] + new_pool_content + content[match.end(2):]
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("Successfully fixed index.tsx using string slicing.")

if __name__ == "__main__":
    fix_index()

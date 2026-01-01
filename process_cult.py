
import re

input_file = r"c:\Users\User\Downloads\zip\культ.md"
output_file = r"c:\Users\User\Downloads\zip\культ_processed.md"

def process_cult_file():
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"Read {len(lines)} lines with utf-8.")
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='cp1251') as f:
            lines = f.readlines()
            print(f"Read {len(lines)} lines with cp1251.")

    items = [] # List of dicts: {'question': text, 'variants': [text, text...]}
    current_question = []
    current_variants = []
    current_variant_text = [] # For multi-line variants
    
    # State machine
    # states: 'init', 'in_question', 'in_variant'
    state = 'init'

    def flush_variant():
        if current_variant_text:
            current_variants.append(" ".join(current_variant_text).strip())
            current_variant_text.clear()

    def flush_item():
        nonlocal current_question, current_variants
        if current_question:
            q_text = " ".join(current_question).strip()
            items.append({'question': q_text, 'variants': list(current_variants)})
            current_question.clear()
            current_variants.clear()

    for line in lines:
        line_s = line.strip()
        
        # Check for tags (both escaped and unescaped)
        is_question_tag = "<question>" in line or "\\<question\\>" in line
        is_variant_tag = "<variant>" in line or "\\<variant\\>" in line
        
        if is_question_tag:
            flush_variant() # Finish potential previous variant
            flush_item()    # Finish potential previous question block
            
            # Start new question
            # Remove tag
            content = line.replace("\\<question\\>", "").replace("<question>", "").strip()
            if content:
                current_question.append(content)
            state = 'in_question'
            
        elif is_variant_tag:
            flush_variant() # Finish previous variant
            
            # Start new variant
            content = line.replace("\\<variant\\>", "").replace("<variant>", "").strip()
            if content:
                current_variant_text.append(content)
            state = 'in_variant'
            
        else:
            # Continue text depending on state
             if state == 'in_question':
                 if line_s:
                     current_question.append(line_s)
             elif state == 'in_variant':
                 if line_s:
                     current_variant_text.append(line_s)

    # Final flush
    flush_variant()
    flush_item()

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, item in enumerate(items, 1):
            f.write(f"{i}. {item['question']}\n")
            for v in item['variants']:
                f.write(f"{v}\n")
            f.write("\n")

if __name__ == "__main__":
    process_cult_file()

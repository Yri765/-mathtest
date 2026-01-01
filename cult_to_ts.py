
import json
import re

input_file = r"c:\Users\User\Downloads\zip\культ.md"
output_file = r"c:\Users\User\Downloads\zip\cult_questions.tsx"

def to_ts_string(s):
    # Escape backslashes and double quotes
    s = s.replace('\\', '\\\\').replace('"', '\\"')
    # Remove newlines or replace them? Questions might be multiline?
    # Usually questions are single line in the breakdown, but let's join if needed.
    return s.replace('\n', ' ')

def process_to_ts():
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by double newlines to get blocks
    blocks = re.split(r'\n\s*\n', content.strip())
    
    questions_data = []
    
    id_counter = 1
    
    for block in blocks:
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines:
            continue
            
        # First line is question
        question_line = lines[0]
        # Remove leading "1. " number
        question_text = re.sub(r'^\d+\.\s*', '', question_line)
        
        options = lines[1:]
        
        # If no options, skip? Or might be a formatting error.
        # But looking at previous file, there are always options.
        if not options:
            continue
            
        # Heuristic: The first option is set as correct Answer by default as requested/implied necessity
        correct_answer = options[0] if options else ""
        
        q_obj = {
            "id": id_counter,
            "text": question_text,
            "options": options,
            "correctAnswer": correct_answer,
            "type": "theory"
        }
        questions_data.append(q_obj)
        id_counter += 1

    # Generate TS content
    ts_content = "export const QUESTION_POOL = [\n"
    for q in questions_data:
        ts_content += "  {\n"
        ts_content += f"    id: {q['id']},\n"
        ts_content += f"    text: \"{to_ts_string(q['text'])}\",\n"
        ts_content += "    options: [\n"
        for opt in q['options']:
            ts_content += f"      \"{to_ts_string(opt)}\",\n"
        ts_content += "    ],\n"
        ts_content += f"    correctAnswer: \"{to_ts_string(q['correctAnswer'])}\",\n"
        ts_content += f"    type: \"{q['type']}\"\n"
        ts_content += "  },\n"
    ts_content += "];\n"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(ts_content)
    
    print(f"Generated {len(questions_data)} questions.")

if __name__ == "__main__":
    process_to_ts()

import re
import json
import random
import os

def parse_questions(md_path):
    # Use utf-8-sig to handle BOM
    with open(md_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    questions = []
    
    q_pattern = re.compile(r'^(\d+)\.\s+(.*)')
    a_pattern = re.compile(r'^Ответ:\s*(.*)')
    
    current_question = None
    current_type = 'practice' # Default type
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check Section more loosely
        if line.startswith('#'):
            section_name = line.strip('#').strip().lower()
            print(f"Found section: {section_name}")
            if 'теория' in section_name:
                current_type = 'theory'
            else:
                current_type = 'practice'
            continue
            
        # Check Question
        q_match = q_pattern.match(line)
        if q_match:
            q_text = q_match.group(2)
            current_question = {
                'text': q_text,
                'type': current_type
            }
        
        # Check Answer
        a_match = a_pattern.match(line)
        if a_match and current_question:
            current_question['correctAnswer'] = a_match.group(1)
            questions.append(current_question)
            current_question = None

    return questions

def update_index(new_questions):
    ts_path = 'c:/Users/User/Downloads/zip/index.tsx'
    
    all_answers = [q['correctAnswer'] for q in new_questions]
    
    final_questions = []
    for i, q in enumerate(new_questions):
        correct = q['correctAnswer']
        potential = [a for a in all_answers if a != correct]
        # Pick 3 random
        distractors = random.sample(potential, 3) if len(potential) >=3 else potential
        
        options = [correct] + distractors
        random.shuffle(options)
        
        final_q = {
            "id": i + 1,
            "text": q['text'],
            "options": options,
            "correctAnswer": correct,
            "type": q['type']
        }
        final_questions.append(final_q)
        
    json_str = json.dumps(final_questions, ensure_ascii=False, indent=2)
    
    with open(ts_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(r'(const QUESTION_POOL: Question\[\] = )(\[.*?\])(;)', re.DOTALL)
    match = pattern.search(content)
    
    if match:
        new_content = content[:match.start(2)] + json_str + content[match.end(2):]
        with open(ts_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Successfully updated index.tsx with {len(final_questions)} questions.")
        
        # Count types
        theory_count = sum(1 for q in final_questions if q['type'] == 'theory')
        print(f"Theory questions: {theory_count}")
        print(f"Practice questions: {len(final_questions) - theory_count}")
    else:
        print("Could not find QUESTION_POOL in index.tsx")

if __name__ == "__main__":
    md_file = 'c:/Users/User/Downloads/zip/questions_with_answers.md'
    qs = parse_questions(md_file)
    if qs:
        update_index(qs)
    else:
        print("No questions parsed!")

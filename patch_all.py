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
    current_type = 'practice' 
    current_section = 'general'
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check Section
        if line.startswith('#'):
            section_name = line.strip('#').strip()
            current_section = section_name
            print(f"Found section: {section_name}")
            
            if 'теория' in section_name.lower():
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
                'type': current_type,
                'section': current_section
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
    
    # 1. Group answers by section
    answers_by_section = {}
    all_answers = []
    
    for q in new_questions:
        sec = q.get('section', 'general')
        ans = q['correctAnswer']
        
        if sec not in answers_by_section:
            answers_by_section[sec] = []
        
        # Avoid duplicates within section pool to keep probability fair? 
        # Actually set is better to avoid exact duplicate options
        answers_by_section[sec].append(ans)
        all_answers.append(ans)

    # 2. Build final questions with context-aware distractors
    final_questions = []
    for i, q in enumerate(new_questions):
        correct = q['correctAnswer']
        sec = q.get('section', 'general')
        
        # Get potential distractors from same section
        section_pool = answers_by_section.get(sec, [])
        potential = [a for a in section_pool if a != correct]
        # Remove duplicates
        potential = list(set(potential))
        
        # If not enough context answers (need 3), borrow from global pool
        if len(potential) < 3:
            global_pool = [a for a in all_answers if a != correct]
            needed = 3 - len(potential)
            # Prioritize global pool that isn't already in potential
            global_pool = list(set(global_pool) - set(potential))
            if len(global_pool) >= needed:
                potential.extend(random.sample(global_pool, needed))
        
        # Check again if we have enough
        if len(potential) >= 3:
            distractors = random.sample(potential, 3)
        else:
            # Should rarely happen with this dataset
            distractors = potential
            
        options = [correct] + distractors
        random.shuffle(options)
        
        final_q = {
            "id": i + 1,
            "text": q['text'],
            "options": options,
            "correctAnswer": correct,
            "type": q['type']
            # We don't necessarily need to save 'section' to index.tsx unless UI uses it, 
            # but getting the type correct is key.
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
        print("Distractors generated contextually by section.")
    else:
        print("Could not find QUESTION_POOL in index.tsx")

if __name__ == "__main__":
    md_file = 'c:/Users/User/Downloads/zip/questions_with_answers.md'
    qs = parse_questions(md_file)
    if qs:
        update_index(qs)
    else:
        print("No questions parsed!")

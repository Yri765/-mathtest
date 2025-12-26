
import re
import json
import random
import os

def parse_questions(md_path):
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found")
        return []

    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    questions = []
    current_question = None
    
    # Regex for question start: "52. Text"
    question_pattern = re.compile(r'^(\d+)\.\s+(.*)')
    # Regex for answer start: "Ответ: Text"
    answer_pattern = re.compile(r'^Ответ:\s+(.*)')

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        q_match = question_pattern.match(line)
        a_match = answer_pattern.match(line)
        
        if q_match:
            q_text = q_match.group(2)
            current_question = {
                'text': q_text
            }
        
        elif a_match and current_question:
            answer_text = a_match.group(1)
            # Basic cleanup of answer text if needed
            current_question['correctAnswer'] = answer_text
            questions.append(current_question)
            current_question = None
            
    return questions

def update_index(new_questions):
    index_path = 'c:/Users/User/Downloads/zip/index.tsx'
    
    if not os.path.exists(index_path):
        print(f"Error: {index_path} not found")
        return

    # Prepare data for injection
    # Collect all answers for distractors
    all_answers = [q['correctAnswer'] for q in new_questions]
    
    final_questions = []
    for i, q in enumerate(new_questions):
        correct = q['correctAnswer']
        
        # Select 3 distractors
        potential_distractors = [a for a in all_answers if a != correct]
        
        if len(potential_distractors) < 3:
             distractors = potential_distractors + ["Option A", "Option B", "Option C"][:3-len(potential_distractors)]
        else:
            distractors = random.sample(potential_distractors, 3)
            
        options = [correct] + distractors
        random.shuffle(options)
        
        final_q = {
            "id": i + 1,
            "text": q['text'],
            "options": options,
            "correctAnswer": correct
        }
        final_questions.append(final_q)
        
    # Serialize to JSON formatted string
    # ensure_ascii=False allows literal unicode characters (Russian)
    # This will escape backslashes automatically (e.g. \vec -> \\vec)
    json_str = json.dumps(final_questions, ensure_ascii=False, indent=2)
    
    # Read index.tsx
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find the existing array
    # We look for: const QUESTION_POOL: Question[] = [ ... ];
    pattern = re.compile(r'(const QUESTION_POOL: Question\[\] = )(\[.*?\])(;)', re.DOTALL)
    match = pattern.search(content)
    
    if not match:
        print("Could not find QUESTION_POOL definition in index.tsx")
        return

    # Replace using string slicing to act safely with escapes
    # match.group(0) is the whole string "const ... = [...];"
    # match.group(1) is "const ... = "
    # match.group(2) is "[...]"
    # match.group(3) is ";"
    
    new_content = content[:match.start(2)] + json_str + content[match.end(2):]
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Successfully updated index.tsx with {len(final_questions)} questions.")

if __name__ == "__main__":
    md_file = 'c:/Users/User/Downloads/zip/questions_with_answers.md'
    questions = parse_questions(md_file)
    if questions:
        update_index(questions)
    else:
        print("No questions found / parsed.")

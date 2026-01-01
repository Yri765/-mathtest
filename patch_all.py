import re
import json
import random
import os

def parse_questions(md_path):
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
            
        if line.startswith('#'):
            section_name = line.strip('#').strip()
            current_section = section_name
            if 'теория' in section_name.lower():
                current_type = 'theory'
            else:
                current_type = 'practice'
            continue
            
        q_match = q_pattern.match(line)
        if q_match:
            q_text = q_match.group(2)
            current_question = {
                'text': q_text,
                'type': current_type,
                'section': current_section
            }
        
        a_match = a_pattern.match(line)
        if a_match and current_question:
            current_question['correctAnswer'] = a_match.group(1)
            questions.append(current_question)
            current_question = None

    return questions

def classify_answer(ans):
    ans = ans.strip()
    
    # 1. Coordinates / Vectors / Sets
    # Matches: (1;2), {1;2}, [1;2], (-5.5; 0)
    # Must contain delimiters and ; or , with numbers
    if re.search(r'[\(\{\[][\d\.\,\;\s\-\+\\]{2,}[\)\}\]]', ans):
        return 'coordinates'
    if 'vector' in ans.lower() or 'вектор' in ans.lower():
         return 'coordinates'
         
    # 2. Equations / Formulas
    # Must contain = and variables
    if '=' in ans and re.search(r'[xyza-zA-Z]', ans):
        return 'equation'
    
    # 3. Numeric / Short Math Expressions
    # Allow digits, standard math symbols, and common latex: \pm, \sqrt, \frac, \infty, \degree, \pi
    # Also allow simple plain text like "5" or "-10.5" or "±4"
    math_chars = r'[\d\s\.\,\+\-\*\/\^\(\)a-zA-Z\\]'
    special_symbols = ['±', '∞', '∅', '°']
    
    is_mostly_math = True
    for char in ans:
        if char not in special_symbols and not re.match(math_chars, char):
            # Check if it's a Cyrillic character - likely text then
            if re.match(r'[а-яА-Я]', char):
                is_mostly_math = False
                break
                
    if is_mostly_math and len(ans) < 50:
        return 'value'
        
    # 4. Text / Definitions
    return 'text'

def update_index(new_questions):
    ts_path = 'c:/Users/User/Downloads/zip/index.tsx'
    
    # 1. Group answers by Format AND Section to keep context relevance within format
    # e.g. "Algebra - Coordinates", "Analysis - Equation"
    pools = {}
    
    for q in new_questions:
        ans = q['correctAnswer']
        fmt = classify_answer(ans)
        sec = q.get('section', 'general')
        
        # Primary key: Format. Secondary: Section.
        # But maybe just Format is enough? If I have coordinates from Algebra and Analysis, they might look similar.
        # However, user complained about context.
        # Let's try to group by Format first.
        
        if fmt not in pools:
            pools[fmt] = []
        pools[fmt].append(ans)
        
    # 2. Build final questions
    final_questions = []
    for i, q in enumerate(new_questions):
        correct = q['correctAnswer']
        fmt = classify_answer(correct)
        
        # Get pool for this format
        pool = pools.get(fmt, [])
        
        # Filter pool to be distinct from correct answer
        potential = [a for a in pool if a != correct]
        potential = list(set(potential)) # Unique
        
        # If not enough, try to borrow from other formats? No, that defeats the purpose.
        # If not enough, we might have to use SECTION based logic as fallback (mixed formats but same topic).
        if len(potential) < 3:
             # Fallback: get answers from same section regardless of format
             sec = q.get('section', 'general')
             section_pool = [q2['correctAnswer'] for q2 in new_questions if q2.get('section') == sec and q2['correctAnswer'] != correct]
             potential.extend(list(set(section_pool) - set(potential)))
        
        if len(potential) >= 3:
            distractors = random.sample(potential, 3)
        else:
            distractors = potential # Should not happen often
            
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
        print("Distractors generated by FORMAT (coordinates, equation, value, text).")
    else:
        print("Could not find QUESTION_POOL in index.tsx")

if __name__ == "__main__":
    md_file = 'c:/Users/User/Downloads/zip/questions_with_answers.md'
    qs = parse_questions(md_file)
    update_index(qs)

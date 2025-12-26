
import json
import random

def create_qa_file():
    input_path = 'c:/Users/User/Downloads/zip/questions.json'
    output_path = 'c:/Users/User/Downloads/zip/questions_answers.txt'
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        # Shuffle the questions
        random.shuffle(questions)
            
        with open(output_path, 'w', encoding='utf-8') as f:
            for q in questions:
                # Write Answer first, then Question
                f.write(f"{q['correctAnswer']}\n")
                f.write(f"{q['text']}\n")
                f.write("\n") # Only one newline for separation (single blank line)
                
        print(f"Successfully created {output_path} with {len(questions)} shuffled items (1 spacing).")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_qa_file()

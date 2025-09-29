#!/usr/bin/env python3
"""
Quick script to check if trivia questions are in the database
"""

from app_simple import app, db, TriviaQuestion

def check_questions():
    with app.app_context():
        try:
            questions = TriviaQuestion.query.all()
            print(f"✅ Total questions in database: {len(questions)}")
            
            if questions:
                print("\n🧠 Sample questions:")
                for i, q in enumerate(questions[:5]):
                    print(f"{i+1}. {q.question}")
                    print(f"   Category: {q.category}, Difficulty: {q.difficulty}")
                    print(f"   A: {q.option_a}")
                    print(f"   Correct: {q.correct_answer}")
                    print("---")
            else:
                print("❌ No questions found in database!")
                
        except Exception as e:
            print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_questions()
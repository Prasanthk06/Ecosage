#!/usr/bin/env python3
"""
Script to manually insert trivia questions into the database
"""

from app_simple import app, db, TriviaQuestion

def insert_questions():
    with app.app_context():
        try:
            # Clear existing questions first
            TriviaQuestion.query.delete()
            
            # Insert the sample questions
            sample_questions = [
                TriviaQuestion(
                    question="What percentage of the Earth's surface is covered by water?",
                    option_a="60%",
                    option_b="71%", 
                    option_c="85%",
                    option_d="55%",
                    correct_answer="B",
                    category="climate",
                    difficulty="easy",
                    points=40,
                    explanation="About 71% of Earth's surface is covered by water, with oceans containing 97% of all water on Earth."
                ),
                TriviaQuestion(
                    question="Which gas is primarily responsible for global warming?",
                    option_a="Oxygen",
                    option_b="Nitrogen",
                    option_c="Carbon Dioxide",
                    option_d="Hydrogen",
                    correct_answer="C",
                    category="climate",
                    difficulty="easy",
                    points=40,
                    explanation="Carbon dioxide (CO2) is the primary greenhouse gas responsible for global warming, trapping heat in Earth's atmosphere."
                ),
                TriviaQuestion(
                    question="How long does it take for a plastic bottle to decompose in nature?",
                    option_a="10-20 years",
                    option_b="50-80 years",
                    option_c="450-1000 years",
                    option_d="Never decomposes",
                    correct_answer="C",
                    category="waste",
                    difficulty="medium",
                    points=40,
                    explanation="Plastic bottles can take 450-1000 years to decompose, making plastic waste one of the most persistent environmental pollutants."
                ),
                TriviaQuestion(
                    question="What is the most abundant renewable energy source?",
                    option_a="Wind",
                    option_b="Solar",
                    option_c="Hydroelectric",
                    option_d="Geothermal",
                    correct_answer="B",
                    category="energy",
                    difficulty="medium",
                    points=40,
                    explanation="Solar energy is the most abundant renewable energy source, with the sun providing more energy in one hour than the world uses in a year."
                ),
                TriviaQuestion(
                    question="Which country produces the most renewable energy?",
                    option_a="United States",
                    option_b="Germany",
                    option_c="China",
                    option_d="Norway",
                    correct_answer="C",
                    category="energy",
                    difficulty="hard",
                    points=40,
                    explanation="China is the world's largest producer of renewable energy, leading in solar, wind, and hydroelectric power generation."
                ),
                TriviaQuestion(
                    question="What does the '3 R's' of waste management stand for?",
                    option_a="Reduce, Reuse, Recycle",
                    option_b="Remove, Reduce, Restore",
                    option_c="Reduce, Restore, Recycle",
                    option_d="Reuse, Restore, Remove",
                    correct_answer="A",
                    category="waste",
                    difficulty="easy",
                    points=40,
                    explanation="The 3 R's - Reduce, Reuse, Recycle - are the fundamental principles of waste management and environmental conservation."
                ),
                TriviaQuestion(
                    question="Which type of light bulb is most energy-efficient?",
                    option_a="Incandescent",
                    option_b="Fluorescent",
                    option_c="LED",
                    option_d="Halogen",
                    correct_answer="C",
                    category="energy",
                    difficulty="easy",
                    points=40,
                    explanation="LED bulbs are the most energy-efficient, using up to 80% less energy than traditional incandescent bulbs."
                ),
                TriviaQuestion(
                    question="What percentage of global carbon emissions come from transportation?",
                    option_a="14%",
                    option_b="24%",
                    option_c="34%",
                    option_d="44%",
                    correct_answer="A",
                    category="climate",
                    difficulty="hard",
                    points=40,
                    explanation="Transportation accounts for approximately 14% of global greenhouse gas emissions, making it a significant contributor to climate change."
                ),
                TriviaQuestion(
                    question="How much water can a running faucet waste per minute?",
                    option_a="1-2 gallons",
                    option_b="2-3 gallons", 
                    option_c="3-5 gallons",
                    option_d="5-7 gallons",
                    correct_answer="B",
                    category="conservation",
                    difficulty="medium",
                    points=40,
                    explanation="A running faucet can waste 2-3 gallons of water per minute, highlighting the importance of turning off taps when not in use."
                ),
                TriviaQuestion(
                    question="Which ecosystem produces the most oxygen on Earth?",
                    option_a="Rainforests",
                    option_b="Grasslands",
                    option_c="Ocean phytoplankton",
                    option_d="Temperate forests",
                    correct_answer="C",
                    category="nature",
                    difficulty="hard",
                    points=40,
                    explanation="Ocean phytoplankton produces about 50-80% of Earth's oxygen, making marine ecosystems crucial for our planet's breathable atmosphere."
                )
            ]
            
            for question in sample_questions:
                db.session.add(question)
            
            db.session.commit()
            
            # Verify questions were inserted
            total_questions = TriviaQuestion.query.count()
            print(f"✅ Successfully inserted {total_questions} trivia questions!")
            
            # Show first few questions
            questions = TriviaQuestion.query.limit(3).all()
            print("\n🧠 Sample questions:")
            for i, q in enumerate(questions):
                print(f"{i+1}. {q.question}")
                print(f"   Answer: {q.correct_answer} - {getattr(q, f'option_{q.correct_answer.lower()}')}")
                print("---")
                
        except Exception as e:
            print(f"❌ Error inserting questions: {e}")
            db.session.rollback()

if __name__ == "__main__":
    insert_questions()
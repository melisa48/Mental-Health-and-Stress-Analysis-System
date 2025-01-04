# main.py

from mental_health_analyzer import MentalHealthAnalyzer
import json
from datetime import datetime
import logging  # Added this import

def validate_rating(value, min_val=1, max_val=10):
    try:
        rating = int(value)
        if min_val <= rating <= max_val:
            return rating
        print(f"\nPlease enter a number between {min_val} and {max_val}")
        return None
    except ValueError:
        print("\nPlease enter a valid number")
        return None

def get_valid_rating(prompt, min_val=1, max_val=10):
    while True:
        value = input(prompt)
        rating = validate_rating(value, min_val, max_val)
        if rating is not None:
            return rating

def main():
    # Setup logging for main.py
    logging.basicConfig(
        filename='mental_health_system.log',
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )
    
    analyzer = MentalHealthAnalyzer()
    
    while True:
        print("\n=== Mental Health and Stress Analysis System ===")
        print("1. Add New User")
        print("2. Record Daily Assessment")
        print("3. View Analysis")
        print("4. Get Recommendations")
        print("5. Export Report")
        print("6. Exit")
        
        try:
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == '1':
                name = input("Enter name: ")
                while True:
                    try:
                        age = int(input("Enter age: "))
                        if 0 < age < 120:
                            break
                        print("Please enter a valid age between 1 and 120")
                    except ValueError:
                        print("Please enter a valid number for age")
                gender = input("Enter gender: ")
                occupation = input("Enter occupation: ")
                
                user_id = analyzer.add_user(name, age, gender, occupation)
                if user_id:
                    print(f"\nUser successfully added! Your ID is: {user_id}")
                    print("Please save this ID for future assessments.")
                else:
                    print("\nError adding user. Please try again.")
            
            elif choice == '2':
                try:
                    user_id = int(input("Enter your user ID: "))
                    
                    assessment_data = {
                        'stress_level': get_valid_rating("Rate your stress level (1-10): "),
                        'anxiety_score': get_valid_rating("Rate your anxiety level (1-10): "),
                        'sleep_quality': get_valid_rating("Rate your sleep quality (1-10): "),
                        'mood_rating': get_valid_rating("Rate your mood (1-10): "),
                        'energy_level': get_valid_rating("Rate your energy level (1-10): "),
                        'social_interaction_score': get_valid_rating("Rate your social interactions today (1-10): "),
                        'physical_activity_level': get_valid_rating("Rate your physical activity level today (1-10): "),
                        'meditation_minutes': get_valid_rating("Enter minutes spent meditating today: ", 0, 1440)
                    }
                    
                    analyzer.record_assessment(user_id, assessment_data)
                    print("\nAssessment recorded successfully!")
                except ValueError:
                    print("\nPlease enter a valid user ID.")
            
            elif choice == '3':
                try:
                    user_id = int(input("Enter your user ID: "))
                    days = int(input("Enter number of days to analyze (default 30): ") or "30")
                    
                    analysis = analyzer.analyze_trends(user_id, days)
                    if analysis:
                        print("\n=== Analysis Results ===")
                        print(f"Average Stress Level: {analysis['average_stress']:.2f}")
                        print(f"Average Anxiety Level: {analysis['average_anxiety']:.2f}")
                        print(f"Mood Variation: {analysis['mood_variation']:.2f}")
                        print(f"Physical Activity Impact: {analysis['physical_activity_correlation']:.2f}")
                        
                        if analysis['meditation_impact']:
                            print("\nMeditation Impact:")
                            print(f"- On Stress: {analysis['meditation_impact']['stress_correlation']:.2f}")
                            print(f"- On Anxiety: {analysis['meditation_impact']['anxiety_correlation']:.2f}")
                            print(f"- On Mood: {analysis['meditation_impact']['mood_correlation']:.2f}")
                    else:
                        print("\nNot enough data for analysis yet.")
                except ValueError:
                    print("\nPlease enter valid numbers for user ID and days.")
            
            elif choice == '4':
                try:
                    user_id = int(input("Enter your user ID: "))
                    analysis = analyzer.analyze_trends(user_id)
                    
                    if analysis:
                        recommendations = analyzer.generate_recommendations(analysis)
                        if recommendations:
                            print("\n=== Personalized Recommendations ===")
                            for rec in recommendations:
                                print(f"\nCategory: {rec['category']}")
                                print(f"Priority: {rec['priority']}")
                                print(f"Suggestion: {rec['suggestion']}")
                        else:
                            print("\nNo specific recommendations at this time.")
                    else:
                        print("\nNot enough data for recommendations yet.")
                except ValueError:
                    print("\nPlease enter a valid user ID.")
            
            elif choice == '5':
                try:
                    user_id = int(input("Enter your user ID: "))
                    analysis = analyzer.analyze_trends(user_id)
                    
                    if analysis:
                        recommendations = analyzer.generate_recommendations(analysis)
                        report = analyzer.export_report(user_id, analysis, recommendations)
                        
                        # Save report to file
                        filename = f"mental_health_report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        with open(filename, 'w') as f:
                            json.dump(report, f, indent=4)
                        print(f"\nReport exported successfully to {filename}")
                    else:
                        print("\nNot enough data to generate a report yet.")
                except ValueError:
                    print("\nPlease enter a valid user ID.")
            
            elif choice == '6':
                print("\nThank you for using the Mental Health and Stress Analysis System!")
                break
            
            else:
                print("\nInvalid choice. Please try again.")
                
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            logging.error(f"Error in main loop: {str(e)}")

if __name__ == "__main__":
    main()
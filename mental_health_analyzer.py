import sqlite3
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import logging

class MentalHealthAnalyzer:
    def __init__(self, db_name='mental_health.db'):
        self.db_name = db_name
        self.setup_logging()
        self.initialize_database()
        
    def setup_logging(self):
        logging.basicConfig(
            filename='mental_health_analyzer.log',
            level=logging.INFO,
            format='%(asctime)s:%(levelname)s:%(message)s'
        )

    def initialize_database(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Create tables for user data and assessments
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT,
                    age INTEGER,
                    gender TEXT,
                    occupation TEXT,
                    registration_date DATE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assessments (
                    assessment_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    date DATE,
                    stress_level INTEGER,
                    anxiety_score INTEGER,
                    sleep_quality INTEGER,
                    mood_rating INTEGER,
                    energy_level INTEGER,
                    social_interaction_score INTEGER,
                    physical_activity_level INTEGER,
                    meditation_minutes INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            conn.commit()
            logging.info("Database initialized successfully")
        except Exception as e:
            logging.error(f"Database initialization error: {str(e)}")
        finally:
            conn.close()

    def add_user(self, name, age, gender, occupation):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (name, age, gender, occupation, registration_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, age, gender, occupation, datetime.now().date()))
            
            user_id = cursor.lastrowid
            conn.commit()
            logging.info(f"New user added with ID: {user_id}")
            return user_id
        except Exception as e:
            logging.error(f"Error adding user: {str(e)}")
            return None
        finally:
            conn.close()

    def record_assessment(self, user_id, assessment_data):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO assessments (
                    user_id, date, stress_level, anxiety_score,
                    sleep_quality, mood_rating, energy_level,
                    social_interaction_score, physical_activity_level,
                    meditation_minutes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                datetime.now().date(),
                assessment_data['stress_level'],
                assessment_data['anxiety_score'],
                assessment_data['sleep_quality'],
                assessment_data['mood_rating'],
                assessment_data['energy_level'],
                assessment_data['social_interaction_score'],
                assessment_data['physical_activity_level'],
                assessment_data['meditation_minutes']
            ))
            
            conn.commit()
            logging.info(f"Assessment recorded for user {user_id}")
        except Exception as e:
            logging.error(f"Error recording assessment: {str(e)}")
        finally:
            conn.close()

    def analyze_trends(self, user_id, days=30):
        try:
            conn = sqlite3.connect(self.db_name)
            query = f'''
                SELECT *
                FROM assessments
                WHERE user_id = {user_id}
                AND date >= date('now', '-{days} days')
                ORDER BY date
            '''
            
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                return None
            
            analysis = {
                'average_stress': df['stress_level'].mean(),
                'average_anxiety': df['anxiety_score'].mean(),
                'sleep_quality_trend': df['sleep_quality'].rolling(window=7).mean().tolist(),
                'mood_variation': df['mood_rating'].std(),
                'physical_activity_correlation': df['physical_activity_level'].corr(df['mood_rating']),
                'meditation_impact': self._analyze_meditation_impact(df)
            }
            
            return analysis
        except Exception as e:
            logging.error(f"Error analyzing trends: {str(e)}")
            return None
        finally:
            conn.close()

    def _analyze_meditation_impact(self, df):
        # Analyze the impact of meditation on stress and anxiety
        if len(df) < 7:
            return None
            
        meditation_impact = {
            'stress_correlation': df['meditation_minutes'].corr(df['stress_level']),
            'anxiety_correlation': df['meditation_minutes'].corr(df['anxiety_score']),
            'mood_correlation': df['meditation_minutes'].corr(df['mood_rating'])
        }
        
        return meditation_impact

    def generate_recommendations(self, analysis_results):
        recommendations = []
        
        if analysis_results['average_stress'] > 7:
            recommendations.append({
                'category': 'Stress Management',
                'suggestion': 'Consider incorporating daily breathing exercises and progressive muscle relaxation',
                'priority': 'High'
            })
        
        if analysis_results['meditation_impact'] and analysis_results['meditation_impact']['mood_correlation'] > 0.5:
            recommendations.append({
                'category': 'Meditation',
                'suggestion': 'Your data shows meditation positively impacts your mood. Consider increasing session duration',
                'priority': 'Medium'
            })
        
        if analysis_results['physical_activity_correlation'] > 0.4:
            recommendations.append({
                'category': 'Physical Activity',
                'suggestion': 'Exercise shows a positive correlation with your mood. Maintain or increase your current activity level',
                'priority': 'Medium'
            })
        
        return recommendations

    def export_report(self, user_id, analysis_results, recommendations):
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': user_id,
            'analysis_summary': analysis_results,
            'recommendations': recommendations,
            'data_quality': self._assess_data_quality(user_id)
        }
        
        return report

    def _assess_data_quality(self, user_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*), 
                       COUNT(DISTINCT date) 
                FROM assessments 
                WHERE user_id = ?
            ''', (user_id,))
            
            total_records, unique_dates = cursor.fetchone()
            
            quality_metrics = {
                'total_records': total_records,
                'completion_rate': unique_dates / 30 if total_records > 0 else 0,
                'data_consistency': unique_dates == total_records
            }
            
            return quality_metrics
        except Exception as e:
            logging.error(f"Error assessing data quality: {str(e)}")
            return None
        finally:
            conn.close()

"""
EcoSage Backend API - Simplified Version
Environmental sustainability platform backend
"""

import os
import logging
import requests
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ecosage-dev-secret-2024')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration (using SQLite for now)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ecosage.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# Database Models
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(200), nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    organizer = db.Column(db.String(100), nullable=False)
    participants = db.Column(db.Integer, default=0)
    max_participants = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'date': self.date.isoformat(),
            'organizer': self.organizer,
            'participants': self.participants,
            'max_participants': self.max_participants,
            'created_at': self.created_at.isoformat()
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    carbon_points = db.Column(db.Integer, default=0)
    total_impact = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'carbon_points': self.carbon_points,
            'total_impact': self.total_impact,
            'created_at': self.created_at.isoformat()
        }

class TriviaQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', or 'D'
    difficulty = db.Column(db.String(10), default='medium')  # 'easy', 'medium', 'hard'
    category = db.Column(db.String(50), default='general')  # 'climate', 'waste', 'energy', etc.
    points = db.Column(db.Integer, default=40)
    explanation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_json(self):
        return {
            'id': self.id,
            'question': self.question,
            'options': {
                'A': self.option_a,
                'B': self.option_b,
                'C': self.option_c,
                'D': self.option_d
            },
            'difficulty': self.difficulty,
            'category': self.category,
            'points': self.points,
            'explanation': self.explanation
        }
    
    def to_json_with_answer(self):
        data = self.to_json()
        data['correct_answer'] = self.correct_answer
        return data

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    total_score = db.Column(db.Integer, default=0)
    questions_answered = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    time_taken = db.Column(db.Integer)  # in seconds
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'total_score': self.total_score,
            'questions_answered': self.questions_answered,
            'correct_answers': self.correct_answers,
            'accuracy': round((self.correct_answers / max(self.questions_answered, 1)) * 100, 1),
            'time_taken': self.time_taken,
            'completed_at': self.completed_at.isoformat()
        }

# Routes
@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'EcoSage Backend API is running',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all environmental events"""
    try:
        events = Event.query.all()
        return jsonify({
            'success': True,
            'events': [event.to_json() for event in events]
        })
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events', methods=['POST'])
def create_event():
    """Create a new environmental event"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['title', 'date', 'organizer']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Parse date
        try:
            event_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format'}), 400
        
        # Create new event
        event = Event(
            title=data['title'],
            description=data.get('description', ''),
            location=data.get('location', ''),
            date=event_date,
            organizer=data['organizer'],
            max_participants=data.get('max_participants')
        )
        
        db.session.add(event)
        db.session.commit()
        
        logger.info(f"Created event: {event.title}")
        return jsonify({
            'success': True,
            'event': event.to_json(),
            'message': 'Event created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/calculate_carbon', methods=['POST'])
def calculate_carbon():
    """Calculate carbon footprint (simplified version)"""
    try:
        data = request.json
        
        # Simple carbon calculation logic
        total_carbon = 0.0
        calculations = {}
        
        # Transportation
        # Transportation - Handle MILES input
        if 'transportation_miles' in data:
            miles = data['transportation_miles']
            km = miles * 1.60934  # Convert miles to kilometers
            
            # Petrol car emission factor (kg CO2 per km)
            car_factor = 0.192
            
            transport_carbon = km * car_factor
            total_carbon += transport_carbon
            
            calculations['transportation'] = {
                'miles': miles,
                'km': round(km, 2),
                'factor': car_factor,
                'carbon': round(transport_carbon, 2)
            }
        
        # Energy
        # Energy - Handle electricity input
        if 'electricity_kwh' in data:
            kwh = data['electricity_kwh']
            
            # India grid emission factor (kg CO2 per kWh)
            electricity_factor = 0.708
            
            electricity_carbon = kwh * electricity_factor
            total_carbon += electricity_carbon
            
            calculations['electricity'] = {
                'kwh': kwh,
                'factor': electricity_factor,
                'carbon': round(electricity_carbon, 2)
            }
        # Food
        if 'food' in data:
            food = data['food']
            food_factors = {
                'meat': 2.5,  # kg CO2 per serving
                'dairy': 1.2,
                'vegetables': 0.3,
                'grains': 0.5
            }
            
            for food_type, servings in food.items():
                if food_type in food_factors and isinstance(servings, (int, float)):
                    carbon = servings * food_factors[food_type]
                    total_carbon += carbon
                    calculations[f'{food_type}_food'] = {
                        'servings': servings,
                        'factor': food_factors[food_type],
                        'carbon': carbon
                    }
        
        # Generate recommendations based on carbon footprint
        recommendations = []
        if total_carbon > 300:
            recommendations.append("Consider using public transport or cycling more often")
            recommendations.append("Reduce meat consumption and try more plant-based meals")
        elif total_carbon > 150:
            recommendations.append("Switch to renewable energy sources if possible")
            recommendations.append("Try carpooling or combining trips")
        else:
            recommendations.append("Great job! You have a low carbon footprint")
            recommendations.append("Share your sustainable practices with others")
        
        return jsonify({
            'success': True,
            'total_carbon': round(total_carbon, 2),
            'electricity_carbon': round(calculations.get('electricity', {}).get('carbon', 0), 2),
            'transportation_carbon': round(calculations.get('transportation', {}).get('carbon', 0), 2),
            'calculations': calculations,
            'recommendations': recommendations,
            'impact_level': 'high' if total_carbon > 300 else 'medium' if total_carbon > 150 else 'low'
        })
        
    except Exception as e:
        logger.error(f"Error calculating carbon: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/classify', methods=['POST'])
def classify_image():
    """Classify uploaded image using trained AI model"""
    try:
        # Check if image file was uploaded
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No image selected'}), 400
        
        # Read and encode image
        image_data = file.read()
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        # Forward to model server
        try:
            model_url = 'http://127.0.0.1:8080/predictions/waste_classifier'
            payload = {'image': image_b64}
            
            response = requests.post(model_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                model_result = response.json()
                
                # Transform model response to match frontend expectations
                prediction = model_result.get('prediction', 'unknown')
                confidence = model_result.get('confidence', 0.0)
                
                # Map waste types to proper labels and impacts
                waste_mapping = {
                    'cardboard': {
                        'label': 'Cardboard',
                        'impact': 'Positive - Highly recyclable, biodegradable material',
                        'suggestions': ['Recycle in paper/cardboard bin', 'Reuse for storage', 'Compost if clean']
                    },
                    'glass': {
                        'label': 'Glass',
                        'impact': 'Positive - 100% recyclable without quality loss',
                        'suggestions': ['Recycle in glass container', 'Reuse jars and bottles', 'Return bottles for deposit']
                    },
                    'metal': {
                        'label': 'Metal',
                        'impact': 'Positive - Infinitely recyclable, high value material',
                        'suggestions': ['Recycle in metal bin', 'Clean before recycling', 'Separate aluminum from steel']
                    },
                    'paper': {
                        'label': 'Paper', 
                        'impact': 'Neutral - Recyclable but degrades with each cycle',
                        'suggestions': ['Recycle clean paper', 'Use both sides', 'Choose digital alternatives']
                    },
                    'plastic': {
                        'label': 'Plastic',
                        'impact': 'Negative - Can take 500+ years to decompose', 
                        'suggestions': ['Check recycling number', 'Reduce plastic use', 'Choose reusable alternatives']
                    },
                    'trash': {
                        'label': 'General Waste',
                        'impact': 'Negative - Likely to end up in landfill or environment',
                        'suggestions': ['Minimize waste production', 'Look for recyclable alternatives', 'Proper disposal']
                    }
                }
                
                waste_info = waste_mapping.get(prediction, {
                    'label': prediction.title(),
                    'impact': 'Unknown environmental impact',
                    'suggestions': ['Consult local waste management guidelines']
                })
                
                result = {
                    'label': waste_info['label'],
                    'confidence': float(confidence),
                    'environmental_impact': waste_info['impact'],
                    'suggestions': waste_info['suggestions']
                }
                
                logger.info(f"Successfully classified image as: {prediction} ({confidence:.2f})")
                
                return jsonify({
                    'success': True,
                    'classification': result,
                    'message': 'Image classified successfully using trained AI model'
                })
            else:
                logger.error(f"Model server error: {response.status_code}")
                return jsonify({
                    'success': False, 
                    'error': f'Model server responded with status {response.status_code}'
                }), 500
                
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to model server")
            return jsonify({
                'success': False,
                'error': 'AI model server is not available. Please ensure the model server is running on port 8080.'
            }), 503
            
        except requests.exceptions.Timeout:
            logger.error("Model server timeout")
            return jsonify({
                'success': False,
                'error': 'Model server request timed out'
            }), 504
        
    except Exception as e:
        logger.error(f"Error classifying image: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get user leaderboard based on carbon points"""
    try:
        users = User.query.order_by(User.carbon_points.desc()).limit(10).all()
        
        if not users:
            # Create sample users if none exist
            sample_users = [
                User(username='eco_warrior', email='eco@example.com', carbon_points=1250, total_impact=45.2),
                User(username='green_thumb', email='green@example.com', carbon_points=980, total_impact=38.7),
                User(username='climate_hero', email='climate@example.com', carbon_points=856, total_impact=31.4),
            ]
            
            for user in sample_users:
                db.session.add(user)
            db.session.commit()
            
            users = User.query.order_by(User.carbon_points.desc()).limit(10).all()
        
        leaderboard = []
        for i, user in enumerate(users, 1):
            user_data = user.to_json()
            user_data['rank'] = i
            leaderboard.append(user_data)
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard
        })
        
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# Trivia Game API Routes
@app.route('/api/trivia/questions', methods=['GET'])
def get_trivia_questions():
    """Get random trivia questions for the game"""
    try:
        count = request.args.get('count', 10, type=int)
        difficulty = request.args.get('difficulty', 'all')
        category = request.args.get('category', 'all')
        
        query = TriviaQuestion.query
        
        if difficulty != 'all':
            query = query.filter(TriviaQuestion.difficulty == difficulty)
        if category != 'all':
            query = query.filter(TriviaQuestion.category == category)
            
        # Get random questions
        questions = query.order_by(db.func.random()).limit(count).all()
        
        return jsonify({
            'success': True,
            'questions': [q.to_json() for q in questions]
        })
        
    except Exception as e:
        logger.error(f"Error getting trivia questions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trivia/submit-answer', methods=['POST'])
def submit_trivia_answer():
    """Submit answer and get result"""
    try:
        data = request.json
        question_id = data.get('question_id')
        user_answer = data.get('answer')
        
        question = TriviaQuestion.query.get(question_id)
        if not question:
            return jsonify({'success': False, 'error': 'Question not found'}), 404
        
        is_correct = question.correct_answer == user_answer.upper()
        points_earned = question.points if is_correct else -10
        
        return jsonify({
            'success': True,
            'correct': is_correct,
            'correct_answer': question.correct_answer,
            'points_earned': points_earned,
            'explanation': question.explanation,
            'question': question.to_json_with_answer()
        })
        
    except Exception as e:
        logger.error(f"Error submitting trivia answer: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trivia/save-score', methods=['POST'])
def save_game_score():
    """Save game session results"""
    try:
        data = request.json
        
        session = GameSession(
            username=data.get('username'),
            total_score=data.get('total_score', 0),
            questions_answered=data.get('questions_answered', 0),
            correct_answers=data.get('correct_answers', 0),
            time_taken=data.get('time_taken', 0)
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Score saved successfully',
            'session_id': session.id
        })
        
    except Exception as e:
        logger.error(f"Error saving game score: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trivia/leaderboard', methods=['GET'])
def get_trivia_leaderboard():
    """Get trivia game leaderboard"""
    try:
        # Get top scores (best score per username)
        subquery = db.session.query(
            GameSession.username,
            db.func.max(GameSession.total_score).label('best_score')
        ).group_by(GameSession.username).subquery()
        
        # Get the actual sessions with best scores
        best_sessions = db.session.query(GameSession)\
            .join(subquery, db.and_(
                GameSession.username == subquery.c.username,
                GameSession.total_score == subquery.c.best_score
            ))\
            .order_by(GameSession.total_score.desc())\
            .limit(10)\
            .all()
        
        leaderboard = []
        for rank, session in enumerate(best_sessions, 1):
            leaderboard.append({
                'rank': rank,
                'username': session.username,
                'score': session.total_score,
                'accuracy': session.correct_answers / max(session.questions_answered, 1) * 100,
                'questions_answered': session.questions_answered,
                'completed_at': session.completed_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard
        })
        
    except Exception as e:
        logger.error(f"Error getting trivia leaderboard: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trivia/stats', methods=['GET'])
def get_trivia_stats():
    """Get overall trivia statistics"""
    try:
        total_questions = TriviaQuestion.query.count()
        total_sessions = GameSession.query.count()
        
        avg_score = db.session.query(db.func.avg(GameSession.total_score)).scalar() or 0
        highest_score = db.session.query(db.func.max(GameSession.total_score)).scalar() or 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_questions': total_questions,
                'total_games_played': total_sessions,
                'average_score': round(avg_score, 1),
                'highest_score': highest_score
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting trivia stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save-fcm-token', methods=['POST'])
def save_fcm_token():
    """Save Firebase Cloud Messaging token for push notifications"""
    try:
        data = request.json
        token = data.get('token')
        user_email = data.get('userEmail', 'user@example.com')
        
        # TODO: Save token to database associated with user
        # For now, just log it
        logger.info(f"📱 FCM Token received for {user_email}: {token[:20]}...")
        
        return jsonify({
            'success': True,
            'message': 'FCM token saved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error saving FCM token: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send-email-notification', methods=['POST'])
def send_email_notification():
    """Send email notification to user's Gmail"""
    try:
        data = request.json
        notification_type = data.get('type', 'general')
        title = data.get('title', 'EcoSage Notification')
        message = data.get('message', 'You have a new notification')
        user_email = data.get('userEmail', 'user@example.com')
        
        # Email configuration (you'll need to set these environment variables)
        SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
        EMAIL_USER = os.getenv('EMAIL_USER', 'your-ecosage-email@gmail.com')
        EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-app-password')
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_USER
        msg['To'] = user_email
        msg['Subject'] = title
        
        # Create HTML email content based on notification type
        html_content = create_email_template(notification_type, title, message, data)
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, user_email, msg.as_string())
        
        logger.info(f"📧 Email notification sent to {user_email}")
        
        return jsonify({
            'success': True,
            'message': f'Email notification sent to {user_email}'
        })
        
    except Exception as e:
        logger.error(f"Error sending email notification: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def create_email_template(notification_type, title, message, data):
    """Create HTML email template based on notification type"""
    
    # Base HTML template
    base_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #4CAF50, #2E7D32); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            .button {{ display: inline-block; background: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            .emoji {{ font-size: 24px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><span class="emoji">🌱</span> EcoSage</h1>
                <p>Your Environmental Companion</p>
            </div>
            <div class="content">
                <h2>{title}</h2>
                <p>{message}</p>
                {get_type_specific_content(notification_type, data)}
                <p>Thank you for being part of the EcoSage community! Together, we're making the world more sustainable.</p>
            </div>
            <div class="footer">
                <p>© 2025 EcoSage | Making sustainability simple</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return base_template

def get_type_specific_content(notification_type, data):
    """Get type-specific content for email templates"""
    
    if notification_type == 'waste_collection':
        return f"""
        <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h3>🗑️ Waste Collection Details</h3>
            <p><strong>Type:</strong> {data.get('wasteType', 'General')} Collection</p>
            <p><strong>Date:</strong> {data.get('date', 'Tomorrow')}</p>
            <p><strong>Reminder Time:</strong> {data.get('time', '19:00')}</p>
            <p style="color: #2e7d32;"><strong>💡 Tip:</strong> Prepare your bins the night before!</p>
        </div>
        """
    
    elif notification_type == 'challenge_nudge':
        challenge_type = data.get('challengeType', 'eco_friendly').replace('_', ' ').title()
        return f"""
        <div style="background: #fff3e0; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h3>💪 Daily Challenge: {challenge_type}</h3>
            <p>Today's mission is to make a positive environmental impact!</p>
            <p style="color: #f57c00;"><strong>🎯 Goal:</strong> Complete this challenge and help protect our planet!</p>
        </div>
        """
    
    elif notification_type == 'community_event':
        return f"""
        <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h3>🎉 Community Event</h3>
            <p><strong>Event:</strong> {data.get('eventName', 'Environmental Event')}</p>
            <p><strong>Location:</strong> {data.get('location', 'Community Center')}</p>
            <p><strong>Time:</strong> Starting in {data.get('timeUntil', '1 hour')}</p>
            <p style="color: #1976d2;"><strong>🤝 Join us and make a difference!</strong></p>
        </div>
        """
    
    else:  # welcome or general
        return f"""
        <div style="background: #f3e5f5; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h3>🎊 Welcome to EcoSage Notifications!</h3>
            <p>You'll now receive:</p>
            <ul>
                <li>🗑️ Waste collection reminders</li>
                <li>🎉 Community event alerts</li>
                <li>💪 Daily eco-challenges</li>
                <li>🌱 Sustainability tips</li>
            </ul>
        </div>
        """

def create_tables():
    """Create database tables"""
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Create sample events if none exist
            if Event.query.count() == 0:
                sample_events = [
                    Event(
                        title="Community Tree Planting Day",
                        description="Join us for a day of planting trees in the local park. Help make our community greener!",
                        location="Central Park",
                        date=datetime.utcnow() + timedelta(days=7),
                        organizer="Green Community Initiative",
                        max_participants=50
                    ),
                    Event(
                        title="Beach Cleanup Drive",
                        description="Help clean up our beautiful beaches and protect marine life.",
                        location="Sunset Beach",
                        date=datetime.utcnow() + timedelta(days=14),
                        organizer="Ocean Guardians",
                        max_participants=30
                    ),
                    Event(
                        title="Renewable Energy Workshop",
                        description="Learn about solar panels, wind energy, and how to make your home more sustainable.",
                        location="Community Center",
                        date=datetime.utcnow() + timedelta(days=21),
                        organizer="Sustainable Future Society",
                        max_participants=25
                    )
                ]
                
                for event in sample_events:
                    db.session.add(event)
                
                # Create sample trivia questions if they don't exist
                if TriviaQuestion.query.count() == 0:
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
                logger.info("Sample events and trivia questions created successfully")
                
        except Exception as e:
            logger.error(f"Error creating tables: {e}")

if __name__ == '__main__':
    # Create tables
    create_tables()
    
    # Start the server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting EcoSage Backend API on port {port}")
    logger.info(f"📱 Frontend should connect to: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
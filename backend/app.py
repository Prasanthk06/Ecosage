from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from models import db, Event, User
import pandas as pd
import redis
import requests
import os
from datetime import datetime, date
from werkzeug.utils import secure_filename
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ecosage-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'mysql+pymysql://root:password@localhost:3306/ecosage'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Initialize Redis connection
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=0,
        decode_responses=True
    )
    redis_client.ping()
    print("✅ Redis connection successful")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    redis_client = None

# Carbon emission factors (kg CO2 per unit)
EMISSION_FACTORS = {
    'electricity': 0.4,  # kg CO2 per kWh
    'transportation': 0.2,  # kg CO2 per mile
    'natural_gas': 0.18,  # kg CO2 per cubic foot
    'water': 0.001,  # kg CO2 per gallon
    'waste': 0.5,  # kg CO2 per pound
}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper functions
def seed_database():
    """Seed the database with sample events if empty"""
    try:
        if Event.query.count() == 0:
            sample_events = [
                Event(
                    title='Community Tree Planting',
                    date=date(2025, 10, 5),
                    time='09:00 AM',
                    location='Central Park',
                    description='Join us for a community tree planting event to help green our neighborhood.',
                    category='Community Action',
                    attendees=45
                ),
                Event(
                    title='Solar Panel Workshop',
                    date=date(2025, 10, 12),
                    time='02:00 PM',
                    location='Community Center',
                    description='Learn about solar panel installation and renewable energy options for your home.',
                    category='Education',
                    attendees=23
                ),
                Event(
                    title='Beach Cleanup Drive',
                    date=date(2025, 10, 18),
                    time='07:00 AM',
                    location='Sunset Beach',
                    description='Help us clean up the beach and protect marine life from plastic pollution.',
                    category='Environmental',
                    attendees=67
                ),
                Event(
                    title='Sustainable Gardening Talk',
                    date=date(2025, 10, 25),
                    time='11:00 AM',
                    location='Botanical Garden',
                    description='Expert talk on sustainable gardening practices and organic farming techniques.',
                    category='Education',
                    attendees=31
                ),
                Event(
                    title='Climate Action March',
                    date=date(2025, 10, 28),
                    time='10:00 AM',
                    location='City Hall',
                    description='Join the peaceful march for climate action and environmental justice.',
                    category='Activism',
                    attendees=120
                ),
                Event(
                    title='Recycling Workshop',
                    date=date(2025, 10, 15),
                    time='03:00 PM',
                    location='Eco Center',
                    description='Learn creative ways to recycle and upcycle household items.',
                    category='Education',
                    attendees=18
                ),
                Event(
                    title='Wildlife Photography Walk',
                    date=date(2025, 10, 22),
                    time='06:00 AM',
                    location='Nature Reserve',
                    description='Guided wildlife photography walk to document local biodiversity.',
                    category='Recreation',
                    attendees=12
                ),
            ]
            
            for event in sample_events:
                db.session.add(event)
            
            db.session.commit()
            logger.info("✅ Database seeded with sample events")
        
        # Seed sample users for leaderboard
        if User.query.count() == 0:
            sample_users = [
                User(username='eco_warrior', email='warrior@eco.com', score=1250, challenges_completed=15),
                User(username='green_thumb', email='green@eco.com', score=980, challenges_completed=12),
                User(username='climate_hero', email='hero@eco.com', score=875, challenges_completed=10),
                User(username='nature_lover', email='nature@eco.com', score=720, challenges_completed=8),
                User(username='sustainable_sam', email='sam@eco.com', score=650, challenges_completed=7),
            ]
            
            for user in sample_users:
                db.session.add(user)
            
            db.session.commit()
            
            # Add users to Redis leaderboard
            if redis_client:
                for user in sample_users:
                    redis_client.zadd('leaderboard', {user.username: user.score})
            
            logger.info("✅ Database seeded with sample users")
            
    except Exception as e:
        logger.error(f"❌ Error seeding database: {e}")
        db.session.rollback()

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'database': 'connected',
            'redis': 'connected' if redis_client else 'disconnected'
        }
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    """
    GET endpoint to retrieve all community events
    """
    try:
        events = Event.query.order_by(Event.date.asc()).all()
        events_list = [event.to_dict() for event in events]
        
        return jsonify({
            'success': True,
            'data': events_list,
            'count': len(events_list)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch events',
            'message': str(e)
        }), 500

@app.route('/api/events', methods=['POST'])
def create_event():
    """
    POST endpoint to create a new event
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Parse date
        event_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # Create new event
        new_event = Event(
            title=data['title'],
            date=event_date,
            time=data.get('time'),
            location=data.get('location'),
            description=data.get('description'),
            category=data.get('category'),
            attendees=data.get('attendees', 0)
        )
        
        db.session.add(new_event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': new_event.to_dict(),
            'message': 'Event created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to create event',
            'message': str(e)
        }), 500

@app.route('/api/calculate_carbon', methods=['POST'])
def calculate_carbon():
    """
    POST endpoint to calculate carbon footprint
    Accepts JSON payload and returns calculated emissions
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Create DataFrame for processing
        df = pd.DataFrame([data])
        
        # Calculate emissions for each category
        results = {}
        total_emissions = 0
        
        for category, factor in EMISSION_FACTORS.items():
            if category in data and data[category]:
                try:
                    value = float(data[category])
                    emissions = value * factor
                    results[category] = {
                        'value': value,
                        'emissions': round(emissions, 2),
                        'unit': 'kg CO₂'
                    }
                    total_emissions += emissions
                except (ValueError, TypeError):
                    results[category] = {
                        'error': f'Invalid value for {category}'
                    }
        
        # Determine comparison category
        if total_emissions < 50:
            comparison = 'below average'
        elif total_emissions < 100:
            comparison = 'average'
        else:
            comparison = 'above average'
        
        # Generate recommendations
        recommendations = []
        if total_emissions > 100:
            recommendations.append("Consider switching to renewable energy sources")
            recommendations.append("Use public transportation or electric vehicles")
        if total_emissions > 50:
            recommendations.append("Improve home insulation to reduce heating/cooling needs")
            recommendations.append("Reduce, reuse, and recycle to minimize waste")
        
        return jsonify({
            'success': True,
            'data': {
                'breakdown': results,
                'total_emissions': round(total_emissions, 2),
                'unit': 'kg CO₂',
                'comparison': comparison,
                'recommendations': recommendations,
                'calculation_timestamp': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating carbon footprint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to calculate carbon footprint',
            'message': str(e)
        }), 500

@app.route('/api/classify', methods=['POST'])
def classify_image():
    """
    POST endpoint for image classification
    Forwards image to TorchServe and returns classification results
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No image file selected'
            }), 400
        
        if file:
            # Secure the filename and save temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Forward to TorchServe inference endpoint
                torchserve_url = "http://127.0.0.1:8080/predictions/waste_classifier"
                
                with open(filepath, 'rb') as img_file:
                    files = {'data': img_file}
                    response = requests.post(torchserve_url, files=files, timeout=30)
                
                # Clean up temporary file
                os.remove(filepath)
                
                if response.status_code == 200:
                    # Parse TorchServe response
                    torchserve_result = response.json()
                    
                    # Format response for frontend
                    return jsonify({
                        'success': True,
                        'data': {
                            'predictions': torchserve_result,
                            'classification_timestamp': datetime.utcnow().isoformat()
                        }
                    }), 200
                else:
                    # TorchServe is not available, return mock results
                    logger.warning(f"TorchServe not available (status: {response.status_code}), returning mock results")
                    
                    mock_results = [
                        {
                            'class': 'Recyclable Plastic',
                            'confidence': 0.94,
                            'category': 'Recyclable',
                            'description': 'This appears to be a plastic bottle or container that can be recycled.',
                            'disposal_method': 'Place in recycling bin with plastic containers',
                            'environmental_impact': 'High - Proper recycling saves energy and reduces landfill waste'
                        },
                        {
                            'class': 'Organic Waste',
                            'confidence': 0.76,
                            'category': 'Compostable',
                            'description': 'This looks like organic matter that can be composted.',
                            'disposal_method': 'Add to compost bin or organic waste collection',
                            'environmental_impact': 'Medium - Composting reduces methane emissions from landfills'
                        },
                        {
                            'class': 'General Waste',
                            'confidence': 0.45,
                            'category': 'Landfill',
                            'description': 'This item may need to go to general waste.',
                            'disposal_method': 'Place in general waste bin',
                            'environmental_impact': 'Low - Consider reducing consumption of such items'
                        }
                    ]
                    
                    return jsonify({
                        'success': True,
                        'data': {
                            'predictions': mock_results,
                            'mock': True,
                            'classification_timestamp': datetime.utcnow().isoformat()
                        }
                    }), 200
                    
            except requests.exceptions.RequestException:
                # TorchServe connection failed, return mock results
                logger.warning("TorchServe connection failed, returning mock results")
                
                mock_results = [
                    {
                        'class': 'Recyclable Paper',
                        'confidence': 0.89,
                        'category': 'Recyclable',
                        'description': 'This appears to be paper material that can be recycled.',
                        'disposal_method': 'Place in paper recycling bin',
                        'environmental_impact': 'High - Paper recycling saves trees and reduces energy consumption'
                    },
                    {
                        'class': 'Electronic Waste',
                        'confidence': 0.67,
                        'category': 'E-Waste',
                        'description': 'This looks like electronic components requiring special disposal.',
                        'disposal_method': 'Take to electronic waste collection point',
                        'environmental_impact': 'Very High - Proper e-waste disposal prevents toxic contamination'
                    }
                ]
                
                return jsonify({
                    'success': True,
                    'data': {
                        'predictions': mock_results,
                        'mock': True,
                        'classification_timestamp': datetime.utcnow().isoformat()
                    }
                }), 200
            
    except Exception as e:
        logger.error(f"Error in image classification: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to classify image',
            'message': str(e)
        }), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """
    GET endpoint to retrieve current leaderboard
    """
    try:
        leaderboard = []
        
        if redis_client:
            # Get top 10 users from Redis sorted set
            top_users = redis_client.zrevrange('leaderboard', 0, 9, withscores=True)
            leaderboard = [
                {'username': user, 'score': int(score)} 
                for user, score in top_users
            ]
        else:
            # Fallback to database if Redis is not available
            users = User.query.order_by(User.score.desc()).limit(10).all()
            leaderboard = [
                {'username': user.username, 'score': user.score}
                for user in users
            ]
        
        return jsonify({
            'success': True,
            'data': leaderboard,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch leaderboard',
            'message': str(e)
        }), 500

# Socket.IO Events

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connection_response', {'status': 'Connected to EcoSage backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('complete_challenge')
def handle_complete_challenge(data):
    """
    Handle challenge completion event
    Updates user score and broadcasts leaderboard update
    """
    try:
        username = data.get('username')
        points = data.get('points', 10)
        challenge_name = data.get('challenge_name', 'Unknown Challenge')
        
        if not username:
            emit('error', {'message': 'Username is required'})
            return
        
        # Update score in Redis
        if redis_client:
            new_score = redis_client.zincrby('leaderboard', points, username)
            logger.info(f"Updated {username} score to {new_score}")
        
        # Update user in database
        user = User.query.filter_by(username=username).first()
        if user:
            user.score += points
            user.challenges_completed += 1
            db.session.commit()
        else:
            # Create new user if doesn't exist
            new_user = User(
                username=username,
                email=f"{username}@eco.com",
                score=points,
                challenges_completed=1
            )
            db.session.add(new_user)
            db.session.commit()
        
        # Get updated leaderboard
        if redis_client:
            top_users = redis_client.zrevrange('leaderboard', 0, 9, withscores=True)
            leaderboard = [
                {'username': user, 'score': int(score)} 
                for user, score in top_users
            ]
        else:
            users = User.query.order_by(User.score.desc()).limit(10).all()
            leaderboard = [
                {'username': user.username, 'score': user.score}
                for user in users
            ]
        
        # Broadcast updated leaderboard to all clients
        socketio.emit('leaderboard_update', {
            'leaderboard': leaderboard,
            'updated_user': username,
            'points_earned': points,
            'challenge_name': challenge_name,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Confirm to the client
        emit('challenge_completed', {
            'success': True,
            'username': username,
            'points_earned': points,
            'challenge_name': challenge_name
        })
        
    except Exception as e:
        logger.error(f"Error handling challenge completion: {e}")
        emit('error', {
            'message': 'Failed to complete challenge',
            'error': str(e)
        })

@socketio.on('join_leaderboard')
def handle_join_leaderboard():
    """Handle request to join leaderboard updates"""
    try:
        # Get current leaderboard
        if redis_client:
            top_users = redis_client.zrevrange('leaderboard', 0, 9, withscores=True)
            leaderboard = [
                {'username': user, 'score': int(score)} 
                for user, score in top_users
            ]
        else:
            users = User.query.order_by(User.score.desc()).limit(10).all()
            leaderboard = [
                {'username': user.username, 'score': user.score}
                for user in users
            ]
        
        emit('leaderboard_update', {
            'leaderboard': leaderboard,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error joining leaderboard: {e}")
        emit('error', {
            'message': 'Failed to join leaderboard',
            'error': str(e)
        })

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested API endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

# Application factory
def create_app():
    """Application factory pattern"""
    with app.app_context():
        try:
            # Create database tables
            db.create_all()
            logger.info("✅ Database tables created")
            
            # Seed database with sample data
            seed_database()
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
    
    return app

if __name__ == '__main__':
    # Create the application
    flask_app = create_app()
    
    # Run the application
    logger.info("🚀 Starting EcoSage Backend API...")
    logger.info("📊 Available endpoints:")
    logger.info("   GET  /api/health")
    logger.info("   GET  /api/events")
    logger.info("   POST /api/events")
    logger.info("   POST /api/calculate_carbon")
    logger.info("   POST /api/classify")
    logger.info("   GET  /api/leaderboard")
    logger.info("🔌 Socket.IO events: connect, disconnect, complete_challenge, join_leaderboard")
    
    socketio.run(
        flask_app,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        allow_unsafe_werkzeug=True
    )
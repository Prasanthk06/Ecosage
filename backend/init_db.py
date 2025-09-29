"""
Database initialization and migration script for EcoSage
"""

from app import create_app
from models import db, Event, User
from datetime import date
import os

def init_database():
    """Initialize database with tables and sample data"""
    
    app = create_app()
    
    with app.app_context():
        print("🗄️  Creating database tables...")
        
        # Drop all tables (for development)
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("✅ Database tables created successfully")
        
        # Add sample events
        print("📅 Adding sample events...")
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
            )
        ]
        
        for event in sample_events:
            db.session.add(event)
        
        # Add sample users
        print("👥 Adding sample users...")
        sample_users = [
            User(username='eco_warrior', email='warrior@eco.com', score=1250, challenges_completed=15),
            User(username='green_thumb', email='green@eco.com', score=980, challenges_completed=12),
            User(username='climate_hero', email='hero@eco.com', score=875, challenges_completed=10),
        ]
        
        for user in sample_users:
            db.session.add(user)
        
        db.session.commit()
        
        print("✅ Sample data added successfully")
        print("🚀 Database initialization complete!")

if __name__ == '__main__':
    init_database()
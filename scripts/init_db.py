"""
Database initialization script for Medical Referral System
Run this script to set up the database and create default admin user
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import create_tables, SessionLocal
from utils.database_helpers import create_default_admin_user

def initialize_database():
    """Initialize database with tables and default data"""
    
    print("🏥 Initializing Medical Referral System Database...")
    
    try:
        # Create all tables
        print("📊 Creating database tables...")
        create_tables()
        print("✅ Database tables created successfully")
        
        # Create default admin user
        print("👤 Creating default admin user...")
        db = SessionLocal()
        try:
            admin_user = create_default_admin_user(db)
            print(f"✅ Admin user created: {admin_user.username}")
            print(f"🔑 Default password: hospital123")
            print("⚠️  Please change the default password in production!")
        finally:
            db.close()
        
        print("\n🎉 Database initialization completed successfully!")
        print("\n📋 Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start the application: uvicorn app:app --reload")
        print("3. Navigate to: http://localhost:8000/auth/login")
        print("4. Login with: admin / hospital123")
        print("5. Change default password in production")
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    initialize_database()
import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.database import db
from src.routes.auth import auth_bp
from src.routes.patient import patient_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'surgery-app-secret-key-change-in-production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Enable CORS for development
CORS(app, supports_credentials=True)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(patient_bp, url_prefix='/api')

# Database configuration
# Use PostgreSQL if DATABASE_URL is set (production), otherwise use SQLite (development)
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Render provides DATABASE_URL starting with postgres://, but SQLAlchemy needs postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Development: use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialize database
db.init_app(app)

with app.app_context():
    # Import all models to ensure they're registered
    from src.models.auth import User, InviteToken
    from src.models.patient import Patient, ClinicVisit, WardAdmission, Surgery, EmergencyCase
    
    # Create all tables
    db.create_all()
    
    # Create default admin if no users exist
    if User.query.count() == 0:
        admin = User(
            username='admin',
            email='admin@surgery.app',
            full_name='المسؤول الرئيسي',
            role='admin',
            specialization='جراحة عامة'
        )
        admin.set_password('admin123')  # Change this password!
        db.session.add(admin)
        db.session.commit()
        print("✓ تم إنشاء حساب المسؤول الافتراضي")
        print("  اسم المستخدم: admin")
        print("  كلمة المرور: admin123")
        print("  ⚠️  يرجى تغيير كلمة المرور فوراً!")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


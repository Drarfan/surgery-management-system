from flask import Blueprint, request, jsonify, session
from src.database import db
from src.models.auth import User, InviteToken
from src.models.patient import Patient
from datetime import datetime, timedelta
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Decorator للتحقق من تسجيل الدخول
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'يجب تسجيل الدخول أولاً'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Decorator للتحقق من صلاحيات المسؤول
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'يجب تسجيل الدخول أولاً'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'صلاحيات المسؤول مطلوبة'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


# ==================== Authentication Routes ====================

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with invite token"""
    try:
        data = request.get_json()
        
        # Check if token is provided
        token_str = data.get('token')
        if not token_str:
            return jsonify({'error': 'رمز الدعوة مطلوب'}), 400
        
        # Verify token
        token = InviteToken.query.filter_by(token=token_str, is_used=False).first()
        if not token:
            return jsonify({'error': 'رمز الدعوة غير صالح أو مستخدم'}), 400
        
        # Check if token expired
        if token.expires_at and token.expires_at < datetime.utcnow():
            return jsonify({'error': 'رمز الدعوة منتهي الصلاحية'}), 400
        
        # Check if username or email already exists
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'error': 'اسم المستخدم موجود مسبقاً'}), 400
        
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'البريد الإلكتروني موجود مسبقاً'}), 400
        
        # Create new user
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            full_name=data.get('full_name'),
            role=token.role,
            specialization=data.get('specialization'),
            phone=data.get('phone')
        )
        user.set_password(data.get('password'))
        
        # Mark token as used
        token.is_used = True
        token.used_by = user.id
        
        db.session.add(user)
        db.session.commit()
        
        # Update token with user id
        token.used_by = user.id
        db.session.commit()
        
        return jsonify({
            'message': 'تم التسجيل بنجاح',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'الحساب غير مفعل'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        
        return jsonify({
            'message': 'تم تسجيل الدخول بنجاح',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'message': 'تم تسجيل الخروج بنجاح'}), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged in user"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'المستخدم غير موجود'}), 404
        
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """Check if user is logged in"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'logged_in': True,
                'user': user.to_dict()
            }), 200
    
    return jsonify({'logged_in': False}), 200


# ==================== Invite Token Routes ====================

@auth_bp.route('/invites', methods=['POST'])
@admin_required
def create_invite():
    """Create a new invite token (Admin only)"""
    try:
        data = request.get_json()
        
        token = InviteToken(
            token=InviteToken.generate_token(),
            created_by=session['user_id'],
            email=data.get('email'),
            role=data.get('role', 'doctor'),
            expires_at=datetime.utcnow() + timedelta(days=7)  # Valid for 7 days
        )
        
        db.session.add(token)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء رابط الدعوة بنجاح',
            'invite': token.to_dict(),
            'invite_link': f'/register?token={token.token}'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/invites', methods=['GET'])
@admin_required
def get_invites():
    """Get all invite tokens (Admin only)"""
    try:
        invites = InviteToken.query.order_by(InviteToken.created_at.desc()).all()
        return jsonify([invite.to_dict() for invite in invites]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/invites/<int:invite_id>', methods=['DELETE'])
@admin_required
def delete_invite(invite_id):
    """Delete an invite token (Admin only)"""
    try:
        invite = InviteToken.query.get_or_404(invite_id)
        db.session.delete(invite)
        db.session.commit()
        return jsonify({'message': 'تم حذف رابط الدعوة'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/invites/verify/<token>', methods=['GET'])
def verify_invite(token):
    """Verify if invite token is valid"""
    try:
        invite = InviteToken.query.filter_by(token=token, is_used=False).first()
        
        if not invite:
            return jsonify({'valid': False, 'error': 'رمز الدعوة غير صالح أو مستخدم'}), 404
        
        if invite.expires_at and invite.expires_at < datetime.utcnow():
            return jsonify({'valid': False, 'error': 'رمز الدعوة منتهي الصلاحية'}), 400
        
        return jsonify({
            'valid': True,
            'role': invite.role,
            'email': invite.email
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== User Management Routes ====================

@auth_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users (Admin only)"""
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user (Admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if data.get('full_name'):
            user.full_name = data.get('full_name')
        if data.get('email'):
            user.email = data.get('email')
        if data.get('specialization'):
            user.specialization = data.get('specialization')
        if data.get('phone'):
            user.phone = data.get('phone')
        if 'is_active' in data:
            user.is_active = data.get('is_active')
        
        db.session.commit()
        return jsonify({
            'message': 'تم تحديث المستخدم بنجاح',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user (Admin only)"""
    try:
        # Prevent admin from deleting themselves
        if user_id == session['user_id']:
            return jsonify({'error': 'لا يمكنك حذف حسابك الخاص'}), 400
        
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف المستخدم بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        user = User.query.get(session['user_id'])
        
        if not user.check_password(data.get('old_password')):
            return jsonify({'error': 'كلمة المرور القديمة غير صحيحة'}), 400
        
        user.set_password(data.get('new_password'))
        db.session.commit()
        
        return jsonify({'message': 'تم تغيير كلمة المرور بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== Setup Admin Account ====================

@auth_bp.route('/setup-admin', methods=['POST'])
def setup_admin():
    """Create initial admin account (only if no users exist)"""
    try:
        # Check if any users exist
        if User.query.count() > 0:
            return jsonify({'error': 'النظام تم إعداده مسبقاً'}), 400
        
        data = request.get_json()
        
        # Create admin user
        admin = User(
            username=data.get('username', 'admin'),
            email=data.get('email'),
            full_name=data.get('full_name'),
            role='admin',
            specialization=data.get('specialization'),
            phone=data.get('phone')
        )
        admin.set_password(data.get('password'))
        
        db.session.add(admin)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء حساب المسؤول بنجاح',
            'user': admin.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


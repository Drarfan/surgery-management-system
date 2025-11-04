from flask import Blueprint, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from src.database import db
from src.models.medical_files import MedicalFile
from src.models.patient import Patient
from src.models.auth import User
from datetime import datetime
import os
import uuid

medical_files_bp = Blueprint('medical_files', __name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'dicom'},
    'pdf': {'pdf'},
    'document': {'doc', 'docx', 'xls', 'xlsx', 'txt'}
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename, file_type):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS.get(file_type, set())

def get_file_type(filename):
    """Determine file type from extension"""
    if '.' not in filename:
        return 'other'
    ext = filename.rsplit('.', 1)[1].lower()
    
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return 'other'


@medical_files_bp.route('/patients/<int:patient_id>/files', methods=['GET'])
def get_patient_files(patient_id):
    """Get all files for a patient"""
    try:
        category = request.args.get('category')
        
        query = MedicalFile.query.filter_by(patient_id=patient_id)
        
        if category:
            query = query.filter_by(category=category)
        
        files = query.order_by(MedicalFile.uploaded_at.desc()).all()
        
        return jsonify([f.to_dict() for f in files]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@medical_files_bp.route('/patients/<int:patient_id>/files/upload', methods=['POST'])
def upload_file(patient_id):
    """Upload a new medical file"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({'error': 'يجب تسجيل الدخول أولاً'}), 401
        
        # Check if patient exists
        patient = Patient.query.get_or_404(patient_id)
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'لم يتم إرفاق ملف'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'لم يتم اختيار ملف'}), 400
        
        # Get form data
        category = request.form.get('category', 'other')
        description = request.form.get('description', '')
        date_taken = request.form.get('date_taken')
        
        # Determine file type
        file_type = get_file_type(file.filename)
        
        # Validate file type
        if not allowed_file(file.filename, file_type):
            return jsonify({'error': 'نوع الملف غير مدعوم'}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}_{patient_id}.{file_ext}"
        
        # Create patient folder
        patient_folder = os.path.join(UPLOAD_FOLDER, f"patient_{patient_id}")
        os.makedirs(patient_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(patient_folder, unique_filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create database record
        medical_file = MedicalFile(
            patient_id=patient_id,
            uploaded_by=session['user_id'],
            file_name=original_filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            mime_type=file.content_type,
            category=category,
            description=description,
            date_taken=datetime.fromisoformat(date_taken) if date_taken else None
        )
        
        db.session.add(medical_file)
        db.session.commit()
        
        return jsonify({
            'message': 'تم رفع الملف بنجاح',
            'file': medical_file.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@medical_files_bp.route('/files/<int:file_id>', methods=['GET'])
def get_file(file_id):
    """Get file details"""
    try:
        medical_file = MedicalFile.query.get_or_404(file_id)
        return jsonify(medical_file.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@medical_files_bp.route('/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    """Download a medical file"""
    try:
        medical_file = MedicalFile.query.get_or_404(file_id)
        
        if not os.path.exists(medical_file.file_path):
            return jsonify({'error': 'الملف غير موجود'}), 404
        
        return send_file(
            medical_file.file_path,
            as_attachment=True,
            download_name=medical_file.file_name
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@medical_files_bp.route('/files/<int:file_id>/view', methods=['GET'])
def view_file(file_id):
    """View a medical file (for images and PDFs)"""
    try:
        medical_file = MedicalFile.query.get_or_404(file_id)
        
        if not os.path.exists(medical_file.file_path):
            return jsonify({'error': 'الملف غير موجود'}), 404
        
        return send_file(
            medical_file.file_path,
            mimetype=medical_file.mime_type
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@medical_files_bp.route('/files/<int:file_id>', methods=['PUT'])
def update_file(file_id):
    """Update file metadata"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'يجب تسجيل الدخول أولاً'}), 401
        
        medical_file = MedicalFile.query.get_or_404(file_id)
        data = request.get_json()
        
        if data.get('category'):
            medical_file.category = data.get('category')
        if data.get('description'):
            medical_file.description = data.get('description')
        if data.get('date_taken'):
            medical_file.date_taken = datetime.fromisoformat(data.get('date_taken'))
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث بيانات الملف بنجاح',
            'file': medical_file.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@medical_files_bp.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a medical file"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'يجب تسجيل الدخول أولاً'}), 401
        
        medical_file = MedicalFile.query.get_or_404(file_id)
        
        # Delete physical file
        if os.path.exists(medical_file.file_path):
            os.remove(medical_file.file_path)
        
        # Delete database record
        db.session.delete(medical_file)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف الملف بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@medical_files_bp.route('/files/categories', methods=['GET'])
def get_categories():
    """Get available file categories"""
    categories = [
        {'value': 'lab_results', 'label': 'نتائج فحوصات'},
        {'value': 'ct_scan', 'label': 'أشعة مقطعية'},
        {'value': 'xray', 'label': 'أشعة سينية'},
        {'value': 'surgical_image', 'label': 'صور جراحية'},
        {'value': 'report', 'label': 'تقرير طبي'},
        {'value': 'other', 'label': 'أخرى'}
    ]
    return jsonify(categories), 200


@medical_files_bp.route('/patients/<int:patient_id>/files/stats', methods=['GET'])
def get_patient_files_stats(patient_id):
    """Get statistics about patient's files"""
    try:
        files = MedicalFile.query.filter_by(patient_id=patient_id).all()
        
        stats = {
            'total': len(files),
            'by_category': {},
            'by_type': {},
            'total_size': 0
        }
        
        for file in files:
            # Count by category
            stats['by_category'][file.category] = stats['by_category'].get(file.category, 0) + 1
            
            # Count by type
            stats['by_type'][file.file_type] = stats['by_type'].get(file.file_type, 0) + 1
            
            # Total size
            stats['total_size'] += file.file_size or 0
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


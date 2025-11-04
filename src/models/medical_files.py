from src.database import db
from datetime import datetime

class MedicalFile(db.Model):
    __tablename__ = 'medical_files'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # File information
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # image, pdf, document
    file_size = db.Column(db.Integer)  # in bytes
    mime_type = db.Column(db.String(100))
    
    # Medical classification
    category = db.Column(db.String(50), nullable=False)  # lab_results, ct_scan, xray, surgical_image, report, other
    description = db.Column(db.Text)
    date_taken = db.Column(db.Date)  # Date when the scan/image was taken
    
    # Metadata
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='medical_files')
    uploader = db.relationship('User', backref='uploaded_files')
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else None,
            'uploaded_by': self.uploaded_by,
            'uploader_name': self.uploader.full_name if self.uploader else None,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'category': self.category,
            'category_ar': self.get_category_arabic(),
            'description': self.description,
            'date_taken': self.date_taken.isoformat() if self.date_taken else None,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }
    
    def get_category_arabic(self):
        categories = {
            'lab_results': 'نتائج فحوصات',
            'ct_scan': 'أشعة مقطعية',
            'xray': 'أشعة سينية',
            'surgical_image': 'صور جراحية',
            'report': 'تقرير طبي',
            'other': 'أخرى'
        }
        return categories.get(self.category, self.category)


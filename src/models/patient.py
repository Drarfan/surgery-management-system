from src.database import db
from datetime import datetime

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20))
    national_id = db.Column(db.String(20), unique=True)
    gender = db.Column(db.String(10))
    blood_type = db.Column(db.String(5))
    allergies = db.Column(db.Text)
    chronic_diseases = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    clinic_visits = db.relationship('ClinicVisit', backref='patient', lazy=True)
    ward_admissions = db.relationship('WardAdmission', backref='patient', lazy=True)
    surgeries = db.relationship('Surgery', backref='patient', lazy=True)
    emergency_cases = db.relationship('EmergencyCase', backref='patient', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'phone': self.phone,
            'national_id': self.national_id,
            'gender': self.gender,
            'blood_type': self.blood_type,
            'allergies': self.allergies,
            'chronic_diseases': self.chronic_diseases,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ClinicVisit(db.Model):
    __tablename__ = 'clinic_visits'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    visit_time = db.Column(db.Time, nullable=False)
    visit_type = db.Column(db.String(50))  # كشف أولي، متابعة، استشارة
    status = db.Column(db.String(20), default='قيد الانتظار')  # قيد الانتظار، مؤكد، ملغي، مكتمل
    complaint = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else None,
            'patient_age': self.patient.age if self.patient else None,
            'patient_phone': self.patient.phone if self.patient else None,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'visit_time': self.visit_time.isoformat() if self.visit_time else None,
            'visit_type': self.visit_type,
            'status': self.status,
            'complaint': self.complaint,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class WardAdmission(db.Model):
    __tablename__ = 'ward_admissions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    admission_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    discharge_date = db.Column(db.DateTime)
    room_number = db.Column(db.String(10))
    bed_number = db.Column(db.String(10))
    diagnosis = db.Column(db.Text)
    condition = db.Column(db.String(50))  # مستقر، جيد، يحتاج متابعة، حرج
    medications = db.Column(db.Text)  # JSON string
    daily_notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='منوم')  # منوم، خرج
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else None,
            'patient_age': self.patient.age if self.patient else None,
            'admission_date': self.admission_date.isoformat() if self.admission_date else None,
            'discharge_date': self.discharge_date.isoformat() if self.discharge_date else None,
            'room_number': self.room_number,
            'bed_number': self.bed_number,
            'diagnosis': self.diagnosis,
            'condition': self.condition,
            'medications': self.medications,
            'daily_notes': self.daily_notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Surgery(db.Model):
    __tablename__ = 'surgeries'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    surgery_type = db.Column(db.String(200), nullable=False)
    surgery_date = db.Column(db.Date, nullable=False)
    surgery_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.String(50))
    operating_room = db.Column(db.String(50))
    anesthesia_type = db.Column(db.String(50))
    status = db.Column(db.String(20), default='مجدولة')  # مجدولة، قيد التحضير، جارية، مكتملة، ملغاة
    pre_op_notes = db.Column(db.Text)
    post_op_notes = db.Column(db.Text)
    complications = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else None,
            'patient_age': self.patient.age if self.patient else None,
            'surgery_type': self.surgery_type,
            'surgery_date': self.surgery_date.isoformat() if self.surgery_date else None,
            'surgery_time': self.surgery_time.isoformat() if self.surgery_time else None,
            'duration': self.duration,
            'operating_room': self.operating_room,
            'anesthesia_type': self.anesthesia_type,
            'status': self.status,
            'pre_op_notes': self.pre_op_notes,
            'post_op_notes': self.post_op_notes,
            'complications': self.complications,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class EmergencyCase(db.Model):
    __tablename__ = 'emergency_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    complaint = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False)  # حرج، عاجل، متوسط، غير عاجل
    status = db.Column(db.String(30), default='في الانتظار')  # في الانتظار، قيد التقييم، قيد العلاج، قيد المراقبة، تم الخروج
    vital_signs = db.Column(db.Text)  # JSON string
    initial_assessment = db.Column(db.Text)
    decision = db.Column(db.String(100))  # تنويم، عملية عاجلة، خروج، تحويل
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else None,
            'patient_age': self.patient.age if self.patient else None,
            'patient_phone': self.patient.phone if self.patient else None,
            'arrival_time': self.arrival_time.isoformat() if self.arrival_time else None,
            'complaint': self.complaint,
            'priority': self.priority,
            'status': self.status,
            'vital_signs': self.vital_signs,
            'initial_assessment': self.initial_assessment,
            'decision': self.decision,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


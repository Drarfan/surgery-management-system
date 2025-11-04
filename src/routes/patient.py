from flask import Blueprint, request, jsonify
from src.database import db
from src.models.patient import Patient, ClinicVisit, WardAdmission, Surgery, EmergencyCase
from datetime import datetime, date, time

patient_bp = Blueprint('patient', __name__)

# ==================== Patient Routes ====================

@patient_bp.route('/patients', methods=['GET'])
def get_patients():
    """Get all patients"""
    try:
        patients = Patient.query.all()
        return jsonify([patient.to_dict() for patient in patients]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get a specific patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        return jsonify(patient.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@patient_bp.route('/patients', methods=['POST'])
def create_patient():
    """Create a new patient"""
    try:
        data = request.get_json()
        patient = Patient(
            name=data.get('name'),
            age=data.get('age'),
            phone=data.get('phone'),
            national_id=data.get('national_id'),
            gender=data.get('gender'),
            blood_type=data.get('blood_type'),
            allergies=data.get('allergies'),
            chronic_diseases=data.get('chronic_diseases')
        )
        db.session.add(patient)
        db.session.commit()
        return jsonify(patient.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update a patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()
        
        patient.name = data.get('name', patient.name)
        patient.age = data.get('age', patient.age)
        patient.phone = data.get('phone', patient.phone)
        patient.national_id = data.get('national_id', patient.national_id)
        patient.gender = data.get('gender', patient.gender)
        patient.blood_type = data.get('blood_type', patient.blood_type)
        patient.allergies = data.get('allergies', patient.allergies)
        patient.chronic_diseases = data.get('chronic_diseases', patient.chronic_diseases)
        
        db.session.commit()
        return jsonify(patient.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== Clinic Visit Routes ====================

@patient_bp.route('/clinic-visits', methods=['GET'])
def get_clinic_visits():
    """Get all clinic visits"""
    try:
        visits = ClinicVisit.query.order_by(ClinicVisit.visit_date.desc()).all()
        return jsonify([visit.to_dict() for visit in visits]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/clinic-visits/<int:visit_id>', methods=['GET'])
def get_clinic_visit(visit_id):
    """Get a specific clinic visit"""
    try:
        visit = ClinicVisit.query.get_or_404(visit_id)
        return jsonify(visit.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@patient_bp.route('/clinic-visits', methods=['POST'])
def create_clinic_visit():
    """Create a new clinic visit"""
    try:
        data = request.get_json()
        visit = ClinicVisit(
            patient_id=data.get('patient_id'),
            visit_date=datetime.strptime(data.get('visit_date'), '%Y-%m-%d').date(),
            visit_time=datetime.strptime(data.get('visit_time'), '%H:%M').time(),
            visit_type=data.get('visit_type'),
            status=data.get('status', 'قيد الانتظار'),
            complaint=data.get('complaint'),
            diagnosis=data.get('diagnosis'),
            treatment=data.get('treatment'),
            notes=data.get('notes')
        )
        db.session.add(visit)
        db.session.commit()
        return jsonify(visit.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/clinic-visits/<int:visit_id>', methods=['PUT'])
def update_clinic_visit(visit_id):
    """Update a clinic visit"""
    try:
        visit = ClinicVisit.query.get_or_404(visit_id)
        data = request.get_json()
        
        if data.get('visit_date'):
            visit.visit_date = datetime.strptime(data.get('visit_date'), '%Y-%m-%d').date()
        if data.get('visit_time'):
            visit.visit_time = datetime.strptime(data.get('visit_time'), '%H:%M').time()
        
        visit.visit_type = data.get('visit_type', visit.visit_type)
        visit.status = data.get('status', visit.status)
        visit.complaint = data.get('complaint', visit.complaint)
        visit.diagnosis = data.get('diagnosis', visit.diagnosis)
        visit.treatment = data.get('treatment', visit.treatment)
        visit.notes = data.get('notes', visit.notes)
        
        db.session.commit()
        return jsonify(visit.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== Ward Admission Routes ====================

@patient_bp.route('/ward-admissions', methods=['GET'])
def get_ward_admissions():
    """Get all ward admissions"""
    try:
        admissions = WardAdmission.query.filter_by(status='منوم').all()
        return jsonify([admission.to_dict() for admission in admissions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/ward-admissions/<int:admission_id>', methods=['GET'])
def get_ward_admission(admission_id):
    """Get a specific ward admission"""
    try:
        admission = WardAdmission.query.get_or_404(admission_id)
        return jsonify(admission.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@patient_bp.route('/ward-admissions', methods=['POST'])
def create_ward_admission():
    """Create a new ward admission"""
    try:
        data = request.get_json()
        admission = WardAdmission(
            patient_id=data.get('patient_id'),
            admission_date=datetime.utcnow(),
            room_number=data.get('room_number'),
            bed_number=data.get('bed_number'),
            diagnosis=data.get('diagnosis'),
            condition=data.get('condition'),
            medications=data.get('medications'),
            daily_notes=data.get('daily_notes'),
            status='منوم'
        )
        db.session.add(admission)
        db.session.commit()
        return jsonify(admission.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/ward-admissions/<int:admission_id>', methods=['PUT'])
def update_ward_admission(admission_id):
    """Update a ward admission"""
    try:
        admission = WardAdmission.query.get_or_404(admission_id)
        data = request.get_json()
        
        admission.room_number = data.get('room_number', admission.room_number)
        admission.bed_number = data.get('bed_number', admission.bed_number)
        admission.diagnosis = data.get('diagnosis', admission.diagnosis)
        admission.condition = data.get('condition', admission.condition)
        admission.medications = data.get('medications', admission.medications)
        admission.daily_notes = data.get('daily_notes', admission.daily_notes)
        admission.status = data.get('status', admission.status)
        
        if data.get('status') == 'خرج' and not admission.discharge_date:
            admission.discharge_date = datetime.utcnow()
        
        db.session.commit()
        return jsonify(admission.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== Surgery Routes ====================

@patient_bp.route('/surgeries', methods=['GET'])
def get_surgeries():
    """Get all surgeries"""
    try:
        surgeries = Surgery.query.order_by(Surgery.surgery_date.desc()).all()
        return jsonify([surgery.to_dict() for surgery in surgeries]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/surgeries/<int:surgery_id>', methods=['GET'])
def get_surgery(surgery_id):
    """Get a specific surgery"""
    try:
        surgery = Surgery.query.get_or_404(surgery_id)
        return jsonify(surgery.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@patient_bp.route('/surgeries', methods=['POST'])
def create_surgery():
    """Create a new surgery"""
    try:
        data = request.get_json()
        surgery = Surgery(
            patient_id=data.get('patient_id'),
            surgery_type=data.get('surgery_type'),
            surgery_date=datetime.strptime(data.get('surgery_date'), '%Y-%m-%d').date(),
            surgery_time=datetime.strptime(data.get('surgery_time'), '%H:%M').time(),
            duration=data.get('duration'),
            operating_room=data.get('operating_room'),
            anesthesia_type=data.get('anesthesia_type'),
            status=data.get('status', 'مجدولة'),
            pre_op_notes=data.get('pre_op_notes'),
            post_op_notes=data.get('post_op_notes'),
            complications=data.get('complications')
        )
        db.session.add(surgery)
        db.session.commit()
        return jsonify(surgery.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/surgeries/<int:surgery_id>', methods=['PUT'])
def update_surgery(surgery_id):
    """Update a surgery"""
    try:
        surgery = Surgery.query.get_or_404(surgery_id)
        data = request.get_json()
        
        if data.get('surgery_date'):
            surgery.surgery_date = datetime.strptime(data.get('surgery_date'), '%Y-%m-%d').date()
        if data.get('surgery_time'):
            surgery.surgery_time = datetime.strptime(data.get('surgery_time'), '%H:%M').time()
        
        surgery.surgery_type = data.get('surgery_type', surgery.surgery_type)
        surgery.duration = data.get('duration', surgery.duration)
        surgery.operating_room = data.get('operating_room', surgery.operating_room)
        surgery.anesthesia_type = data.get('anesthesia_type', surgery.anesthesia_type)
        surgery.status = data.get('status', surgery.status)
        surgery.pre_op_notes = data.get('pre_op_notes', surgery.pre_op_notes)
        surgery.post_op_notes = data.get('post_op_notes', surgery.post_op_notes)
        surgery.complications = data.get('complications', surgery.complications)
        
        db.session.commit()
        return jsonify(surgery.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== Emergency Case Routes ====================

@patient_bp.route('/emergency-cases', methods=['GET'])
def get_emergency_cases():
    """Get all emergency cases"""
    try:
        cases = EmergencyCase.query.filter(EmergencyCase.status != 'تم الخروج').order_by(EmergencyCase.arrival_time.desc()).all()
        return jsonify([case.to_dict() for case in cases]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/emergency-cases/<int:case_id>', methods=['GET'])
def get_emergency_case(case_id):
    """Get a specific emergency case"""
    try:
        case = EmergencyCase.query.get_or_404(case_id)
        return jsonify(case.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@patient_bp.route('/emergency-cases', methods=['POST'])
def create_emergency_case():
    """Create a new emergency case"""
    try:
        data = request.get_json()
        case = EmergencyCase(
            patient_id=data.get('patient_id'),
            arrival_time=datetime.utcnow(),
            complaint=data.get('complaint'),
            priority=data.get('priority'),
            status=data.get('status', 'في الانتظار'),
            vital_signs=data.get('vital_signs'),
            initial_assessment=data.get('initial_assessment'),
            decision=data.get('decision'),
            notes=data.get('notes')
        )
        db.session.add(case)
        db.session.commit()
        return jsonify(case.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/emergency-cases/<int:case_id>', methods=['PUT'])
def update_emergency_case(case_id):
    """Update an emergency case"""
    try:
        case = EmergencyCase.query.get_or_404(case_id)
        data = request.get_json()
        
        case.complaint = data.get('complaint', case.complaint)
        case.priority = data.get('priority', case.priority)
        case.status = data.get('status', case.status)
        case.vital_signs = data.get('vital_signs', case.vital_signs)
        case.initial_assessment = data.get('initial_assessment', case.initial_assessment)
        case.decision = data.get('decision', case.decision)
        case.notes = data.get('notes', case.notes)
        
        db.session.commit()
        return jsonify(case.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== Statistics Routes ====================

@patient_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get dashboard statistics"""
    try:
        today = date.today()
        
        stats = {
            'today_appointments': ClinicVisit.query.filter_by(visit_date=today).count(),
            'ward_patients': WardAdmission.query.filter_by(status='منوم').count(),
            'scheduled_surgeries': Surgery.query.filter(
                Surgery.surgery_date >= today,
                Surgery.status.in_(['مجدولة', 'قيد التحضير'])
            ).count(),
            'emergency_cases': EmergencyCase.query.filter(
                EmergencyCase.status != 'تم الخروج'
            ).count(),
            'total_patients': Patient.query.count()
        }
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


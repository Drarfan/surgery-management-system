# Surgery Management System

A comprehensive web application for general surgery specialists to manage patient care across clinics, surgical wards, operations, and emergency departments.

## Features

### 1. Main Dashboard
- Quick statistics overview
- Upcoming appointments
- Recent notifications

### 2. Outpatient Clinics
- Schedule and manage appointments
- Patient registration
- Diagnosis and treatment records

### 3. Surgical Wards
- Inpatient management
- Daily condition monitoring
- Medication tracking
- Medical notes

### 4. Surgical Operations
- Operation scheduling
- Pre-op and post-op notes
- Anesthesia type tracking
- Operating room management

### 5. Emergency Department
- Emergency case registration
- Priority classification (Critical, Urgent, Medium, Non-urgent)
- Vital signs monitoring
- Medical decision tracking

## Technology Stack

**Frontend:**
- React.js
- Tailwind CSS
- shadcn/ui components
- Lucide icons

**Backend:**
- Flask (Python)
- SQLAlchemy ORM
- SQLite database
- RESTful API

## Installation

### Prerequisites
- Python 3.11 or higher
- Modern web browser

### Steps

1. Navigate to the project directory:
```bash
cd surgery_backend
```

2. Activate virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

3. Install dependencies (if needed):
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python src/main.py
```

5. Open browser and go to:
```
http://localhost:5000
```

## Project Structure

```
surgery_backend/
├── src/
│   ├── models/
│   │   └── patient.py          # Database models
│   ├── routes/
│   │   └── patient.py          # API routes
│   ├── static/                 # Frontend build files
│   ├── database/
│   │   └── app.db             # SQLite database
│   └── main.py                # Application entry point
├── venv/                      # Virtual environment
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## API Endpoints

### Patients
- `GET /api/patients` - Get all patients
- `GET /api/patients/<id>` - Get specific patient
- `POST /api/patients` - Create new patient
- `PUT /api/patients/<id>` - Update patient

### Clinic Visits
- `GET /api/clinic-visits` - Get all clinic visits
- `POST /api/clinic-visits` - Create new visit
- `PUT /api/clinic-visits/<id>` - Update visit

### Ward Admissions
- `GET /api/ward-admissions` - Get all admissions
- `POST /api/ward-admissions` - Create new admission
- `PUT /api/ward-admissions/<id>` - Update admission

### Surgeries
- `GET /api/surgeries` - Get all surgeries
- `POST /api/surgeries` - Create new surgery
- `PUT /api/surgeries/<id>` - Update surgery

### Emergency Cases
- `GET /api/emergency-cases` - Get all emergency cases
- `POST /api/emergency-cases` - Create new case
- `PUT /api/emergency-cases/<id>` - Update case

### Statistics
- `GET /api/statistics` - Get dashboard statistics

## Database Schema

### Patients
- Personal information
- Medical history
- Contact details

### Clinic Visits
- Appointment details
- Diagnosis and treatment
- Visit status

### Ward Admissions
- Room and bed assignment
- Daily condition
- Medications

### Surgeries
- Operation details
- Anesthesia type
- Pre/post-op notes

### Emergency Cases
- Arrival time
- Priority level
- Vital signs
- Medical decisions

## Security Notes

⚠️ **Important:** This application is for demonstration and educational purposes. For production use with real patient data:

- Implement proper authentication and authorization
- Add data encryption
- Follow HIPAA or local healthcare data protection regulations
- Use HTTPS
- Implement proper backup procedures
- Add audit logging

## Future Enhancements

- User authentication system
- PDF report generation
- SMS/Email notifications
- Integration with hospital systems
- Data export to Excel
- Multi-language support
- Mobile app version

## License

This project is for educational purposes.

## Support

For issues or questions, please refer to the documentation or contact the developer.


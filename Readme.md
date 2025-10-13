# 🧠 Brain Tumor Detection Web Application

A professional AI-powered medical diagnostic system for brain tumor detection using deep learning and Grad-CAM visualization. Built for healthcare professionals with secure authentication, patient management, and comprehensive reporting.

## ✨ Features

- 🔐 **Secure Authentication** - Doctor login/signup with medical license verification
- 🤖 **AI-Powered Detection** - ResNet50-based model for brain tumor classification
- 🔥 **Grad-CAM Visualization** - Visual explanation of AI decision-making
- 📊 **Dashboard Analytics** - Real-time statistics and scan history
- 📄 **PDF Reports** - Professional medical reports with patient information
- 💾 **Database Storage** - Complete scan history with patient records
- 🎨 **Modern UI** - Beautiful, responsive interface with Tailwind CSS

## 📁 Project Structure

```
brain-tumor-detection/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── database.py          # Database configuration
│   ├── auth.py              # Authentication logic
│   ├── prediction.py        # ML prediction with Grad-CAM
│   ├── pdf_generator.py     # PDF report generator
│   └── requirements.txt     # Python dependencies
├── model/
│   └── best_model.h5        # Trained model
├── frontend/
│   ├── index.html           # Login page
│   ├── signup.html          # Registration page
│   └── dashboard.html       # Main dashboard
├── uploads/                 # MRI images storage
├── reports/                 # Generated PDF reports
└── database.db              # SQLite database
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- pip package manager
- Modern web browser

### Step 1: Clone/Download Project

Place all files in a directory following the structure above.

### Step 2: Install Python Dependencies

```bash
# Navigate to project directory
cd brain-tumor-detection

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Step 3: Place Your Model

Ensure your trained model `best_model.h5` is in the `model/` folder:
```
model/best_model.h5
```

### Step 4: Create Required Directories

```bash
mkdir uploads
mkdir reports
mkdir static
mkdir static/css
mkdir static/js
mkdir static/assets
```

### Step 5: Start Backend Server

```bash
# From project root directory
cd backend
python main.py
```

The API will start at `http://localhost:8000`

### Step 6: Open Frontend

Open `frontend/index.html` in your web browser, or serve it using:

```bash
# Simple HTTP server (Python)
cd frontend
python -m http.server 8080
```

Then visit: `http://localhost:8080`

## 📖 User Guide

### 1. Registration (First Time)

1. Open the application
2. Click "Sign Up"
3. Enter:
   - Full Name (e.g., Dr. John Smith)
   - Email Address
   - Medical License Number
   - Password (min 6 characters)
4. Click "Create Account"

### 2. Login

1. Enter registered email and password
2. Click "Sign In"
3. You'll be redirected to the dashboard

### 3. Perform Brain Tumor Analysis

1. **Enter Patient Information:**
   - Patient Name
   - Patient ID
   - Clinical Notes (optional)

2. **Upload MRI Image:**
   - Click the upload area or drag & drop
   - Select a brain MRI scan (JPG/PNG)
   - Preview will appear

3. **Analyze:**
   - Click "🔬 Analyze Scan"
   - AI will process the image (takes 5-10 seconds)

4. **View Results:**
   - **Original MRI** - Uploaded scan
   - **Grad-CAM Heatmap** - AI focus areas
   - **Prediction** - Tumor or No Tumor
   - **Confidence** - AI certainty percentage

### 4. Download PDF Report

1. After analysis, click "📄 Download PDF Report"
2. Professional medical report will download with:
   - Patient information
   - Diagnosis results
   - MRI images
   - Grad-CAM visualization
   - Clinical notes
   - Disclaimer

### 5. View History

- Recent scans appear in "📋 Recent Scans"
- Click any scan to view details
- Access all previous analyses

## 🎨 Design Features

### Color Palette
- **Primary Blue**: `#2563eb` - Trust & Medical
- **Success Green**: `#10b981` - Healthy/Negative
- **Danger Red**: `#ef4444` - Alert/Positive
- **Dark Gray**: `#1e293b` - Text
- **Light Gray**: `#f8fafc` - Background

### Typography
- **Font Family**: Inter (Google Fonts)
- **Headings**: Bold, clear hierarchy
- **Body Text**: Readable, professional

### UI Components
- Glass-morphism effects
- Smooth transitions & hover states
- Responsive grid layouts
- Card-based design
- Gradient backgrounds

## 🔧 API Endpoints

### Authentication
- `POST /signup` - Register new doctor
- `POST /login` - Doctor login
- `GET /me` - Get current doctor info

### Predictions
- `POST /predict` - Analyze MRI scan
- `GET /scans` - Get all scans
- `GET /scan/{id}` - Get specific scan
- `GET /download-report/{id}` - Download PDF report

### Statistics
- `GET /stats` - Get dashboard statistics

## 🔒 Security Features

- Password hashing with bcrypt
- JWT token authentication
- Secure session management
- Input validation
- Medical license verification
- Doctor-specific data isolation

## 🗄️ Database Schema

### Doctors Table
- id (Primary Key)
- email (Unique)
- full_name
- license_number (Unique)
- hashed_password
- created_at

### Scans Table
- id (Primary Key)
- doctor_id (Foreign Key)
- patient_name
- patient_id
- image_path
- prediction
- confidence
- gradcam_path
- notes
- scan_date

## 🧪 Testing

### Test Credentials (After Registration)
```
Email: doctor@test.com
Password: test123
Name: Dr. Test User
License: MD-TEST-001
```

### Sample Workflow
1. Register/Login
2. Upload test MRI image
3. Enter patient: "Test Patient", ID: "P-001"
4. Analyze scan
5. Download report
6. Check scan history

## 🐛 Troubleshooting

### Common Issues

**1. "Model not found" error**
- Ensure `model/best_model.h5` exists
- Check file path in `prediction.py`

**2. "Network error" on frontend**
- Verify backend is running on port 8000
- Check `API_URL` in HTML files matches server

**3. "Database locked" error**
- Close any SQLite browser tools
- Restart backend server

**4. Image upload fails**
- Check file size (< 10MB)
- Ensure image format is JPG/PNG
- Verify `uploads/` directory exists

**5. PDF download fails**
- Check `reports/` directory exists
- Ensure ReportLab is installed
- Verify image paths are valid

### Performance Tips

- Use JPG images for faster upload
- Resize large images before upload
- Clear browser cache if UI doesn't update
- Use virtual environment for dependencies

## 📚 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **TensorFlow** - Deep learning inference
- **SQLAlchemy** - Database ORM
- **OpenCV** - Image processing
- **ReportLab** - PDF generation
- **JWT** - Authentication
- **Uvicorn** - ASGI server

### Frontend
- **HTML5** - Structure
- **Tailwind CSS** - Styling
- **JavaScript (Vanilla)** - Interactivity
- **Fetch API** - HTTP requests

### Database
- **SQLite** - Lightweight SQL database

### ML Model
- **ResNet50** - Base architecture
- **Grad-CAM** - Explainable AI

## 🎯 Future Enhancements

- [ ] Multi-class tumor classification
- [ ] 3D MRI scan support
- [ ] Patient portal access
- [ ] Email notifications
- [ ] Cloud storage (AWS S3)
- [ ] Advanced analytics dashboard
- [ ] Export to DICOM format
- [ ] Mobile app version
- [ ] Multi-language support

## ⚠️ Medical Disclaimer

**IMPORTANT**: This application is a diagnostic aid tool and should NOT be used as the sole basis for clinical decisions. All AI predictions must be verified by qualified medical professionals through comprehensive clinical evaluation. This tool is intended for research and educational purposes.

## 📄 License

This project is for educational and research purposes. Ensure compliance with medical regulations (HIPAA, GDPR) before clinical use.

## 👨‍⚕️ For Healthcare Professionals

This system is designed exclusively for licensed medical professionals. Features include:
- Secure patient data handling
- HIPAA-compliant storage considerations
- Professional medical reporting
- Audit trail with timestamps
- Doctor authentication system

## 🤝 Support

For issues or questions:
1. Check troubleshooting section
2. Verify all dependencies installed
3. Ensure model file is present
4. Check backend logs for errors

---

**Built with ❤️ for Healthcare Innovation**

*Version 1.0.0*
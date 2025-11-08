# 🚀 Production-Ready ML Pipeline - Complete Setup

## ✅ What's Included

This project is **production-ready** with:

- ✅ **Automated ML Pipeline** - Runs drift detection, preprocessing, training, evaluation, and notifications
- ✅ **CI/CD with GitHub Actions** - Automated deployment on code/data changes
- ✅ **Docker Containerization** - FastAPI and Streamlit services
- ✅ **Render Hosting** - Cloud deployment configuration
- ✅ **Email Notifications** - Automated alerts for training and drift
- ✅ **Streamlit Interface** - User-friendly web interface
- ✅ **FastAPI Backend** - RESTful API for predictions

## 📁 Project Structure

```
Salary Predictor/
├── app.py                      # FastAPI application
├── streamlit_app.py            # Streamlit web interface
├── automated_pipeline.py      # Complete ML pipeline
├── Dockerfile                  # FastAPI Docker image
├── Dockerfile.streamlit        # Streamlit Docker image
├── docker-compose.yml          # Local development
├── render.yaml                 # Render deployment config
├── .github/workflows/
│   ├── deploy.yml             # Main CI/CD pipeline
│   └── render-deploy.yml      # Render deployment trigger
├── data/
│   ├── salary_data.csv        # Main training data
│   └── new_data/              # New data directory
├── models/
│   ├── model.pkl              # Trained model
│   └── metrics.json           # Model metrics
└── src/
    ├── drift_detector.py      # Data drift detection
    ├── preprocess.py          # Data preprocessing
    ├── train_model.py         # Model training
    ├── evaluate.py            # Model evaluation
    ├── notify.py              # Email notifications
    └── utils.py               # Utility functions
```

## 🎯 Quick Start

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Train model
python src/train_model.py

# Start FastAPI
uvicorn app:app --reload

# Start Streamlit (in another terminal)
streamlit run streamlit_app.py
```

### 2. Production Deployment

See `PRODUCTION_DEPLOYMENT.md` for detailed instructions.

**Quick Steps:**
1. Push code to GitHub
2. Configure GitHub Secrets
3. Deploy to Render using `render.yaml`
4. Enable auto-deploy

## 🔄 How to Trigger Pipeline

### Method 1: Add New Data (Recommended)

```bash
# Place new data
cp new_data.csv data/new_data/latest.csv

# Commit and push
git add data/new_data/latest.csv
git commit -m "Add new training data"
git push origin main
```

**What happens:**
- ✅ GitHub Actions detects new data
- ✅ Runs automated pipeline
- ✅ Trains model
- ✅ Sends email
- ✅ Builds Docker images
- ✅ Deploys to Render

### Method 2: Manual Trigger

1. Go to GitHub → Actions
2. Click "ML Model CI/CD Pipeline"
3. Click "Run workflow"
4. Select options and run

See `HOW_TO_TRIGGER_PIPELINE.md` for all methods.

## 📧 Email Notifications

Configure in GitHub Secrets:
- `SMTP_SERVER`
- `SMTP_PORT`
- `EMAIL_FROM`
- `EMAIL_PASSWORD`
- `EMAIL_TO`

You'll receive emails for:
- ✅ Training success (with metrics)
- ❌ Training failures
- ⚠️ Data drift detected

## 🐳 Docker

### Build Locally

```bash
# FastAPI
docker build -t job-salary-api:latest .

# Streamlit
docker build -f Dockerfile.streamlit -t job-salary-streamlit:latest .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

Access:
- FastAPI: http://localhost:8000
- Streamlit: http://localhost:8501

## 🌐 Render Deployment

### Using Blueprint (Easiest)

1. Push `render.yaml` to GitHub
2. In Render: New → Blueprint
3. Connect repository
4. Click "Apply"

### Manual Setup

1. Create two web services
2. Use `Dockerfile` and `Dockerfile.streamlit`
3. Set environment variables
4. Enable auto-deploy

See `PRODUCTION_DEPLOYMENT.md` for details.

## 📊 Pipeline Flow

```
New Data Added
    ↓
GitHub Actions Triggered
    ↓
Automated Pipeline:
  1. Drift Detection
  2. Data Preprocessing
  3. Data Merge
  4. Model Training
  5. Model Evaluation
  6. Email Notification
    ↓
Docker Build
    ↓
Render Deployment
    ↓
Services Live
```

## 🔍 Monitoring

### GitHub Actions
- View logs: GitHub → Actions → Latest run
- Check each step for errors

### Render Dashboard
- View logs: Dashboard → Service → Logs
- Check health: Service → Events

### Email
- Check inbox for notifications
- Verify metrics in email

## 🚨 Troubleshooting

### Pipeline Not Running?
- ✅ Check file path: `data/new_data/latest.csv`
- ✅ Verify file is committed and pushed
- ✅ Check GitHub Actions is enabled

### Build Failing?
- ✅ Test locally: `python automated_pipeline.py`
- ✅ Check Docker: `docker build -t test .`
- ✅ Verify dependencies: `pip install -r requirements.txt`

### Email Not Sending?
- ✅ Check GitHub Secrets are set
- ✅ Test email: `python -m src.notify "Test" "Test"`
- ✅ Verify SMTP credentials

## 📚 Documentation

- **`PRODUCTION_DEPLOYMENT.md`** - Complete deployment guide
- **`HOW_TO_TRIGGER_PIPELINE.md`** - All trigger methods
- **`DEPLOYMENT_GUIDE.md`** - General deployment info
- **`DRIFT_MONITORING_SETUP.md`** - Drift detection setup
- **`EMAIL_SETUP.md`** - Email configuration

## ✅ Requirements Satisfied

- ✅ **Automated Model Deployment** - CI/CD with GitHub Actions
- ✅ **Docker** - Both FastAPI and Streamlit containerized
- ✅ **FastAPI** - RESTful API backend
- ✅ **Streamlit** - Web interface
- ✅ **Render Hosting** - Production deployment ready
- ✅ **Email Notifications** - Automated alerts
- ✅ **Drift Detection** - Automatic monitoring

## 🎯 Next Steps

1. **Deploy to Render** - Follow `PRODUCTION_DEPLOYMENT.md`
2. **Configure Secrets** - Set up GitHub Secrets
3. **Test Pipeline** - Add new data and verify
4. **Monitor** - Check logs and emails
5. **Scale** - Upgrade Render plan if needed

---

**Ready for Production!** 🚀

For detailed instructions, see the documentation files listed above.


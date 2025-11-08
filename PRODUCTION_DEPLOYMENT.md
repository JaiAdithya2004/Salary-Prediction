# 🚀 Production Deployment Guide - Render + GitHub Actions CI/CD

## 📋 Overview

This guide covers deploying your ML pipeline to production using:
- **Render** - Cloud hosting platform
- **GitHub Actions** - CI/CD automation
- **Docker** - Containerization
- **Automated Pipeline** - ML workflow automation

## 🏗️ Architecture

```
GitHub Repository
    ↓
GitHub Actions (CI/CD)
    ↓
Automated Pipeline (drift → preprocess → train → evaluate → notify)
    ↓
Docker Build & Push
    ↓
Render Deployment
    ├── FastAPI Service (Port 8000)
    └── Streamlit Service (Port 8501)
```

## 🔄 How the Pipeline Works

### Automatic Triggers

The pipeline automatically runs when:

1. **New Data Added**: File pushed to `data/new_data/latest.csv`
2. **Code Changes**: Changes to `src/`, `app.py`, or `data/salary_data.csv`
3. **Manual Trigger**: Via GitHub Actions UI

### Pipeline Steps

1. **Drift Detection** - Compares new vs existing data
2. **Data Merge** - Merges new data with existing dataset
3. **Preprocessing** - Cleans and prepares data
4. **Training** - Trains the ML model
5. **Evaluation** - Calculates model metrics
6. **Notification** - Sends email with results
7. **Docker Build** - Creates container images
8. **Deployment** - Deploys to Render

## 📝 Step-by-Step Setup

### Step 1: GitHub Repository Setup

1. **Push your code to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit - Production ready"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

2. **Configure GitHub Secrets:**

Go to: `Settings → Secrets and variables → Actions`

Add these secrets:

**For Email Notifications:**
- `SMTP_SERVER` - e.g., `smtp.gmail.com`
- `SMTP_PORT` - e.g., `587`
- `EMAIL_FROM` - Your email address
- `EMAIL_PASSWORD` - Your app password
- `EMAIL_TO` - Recipient email

**For Docker Hub (Optional):**
- `DOCKERHUB_USERNAME` - Your Docker Hub username
- `DOCKERHUB_TOKEN` - Your Docker Hub access token

### Step 2: Render Account Setup

1. **Sign up at [render.com](https://render.com)**
2. **Connect your GitHub account**
3. **Create a new Blueprint** (or use individual services)

### Step 3: Deploy to Render

#### Option A: Using Render Blueprint (Recommended)

1. **Push `render.yaml` to your repository**
2. **In Render Dashboard:**
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click "Apply"

#### Option B: Manual Service Creation

**FastAPI Service:**
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `job-salary-api`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
   - **Docker Context**: `.`
   - **Health Check Path**: `/health`
   - **Plan**: Starter ($7/month) or Free
4. Add Environment Variables:
   - `MODEL_PATH`: `models/model.pkl`
   - `PYTHONUNBUFFERED`: `1`
5. Click "Create Web Service"

**Streamlit Service:**
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `job-salary-streamlit`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile.streamlit`
   - **Docker Context**: `.`
   - **Health Check Path**: `/_stcore/health`
   - **Plan**: Starter ($7/month) or Free
4. Add Environment Variables:
   - `API_URL`: `https://job-salary-api.onrender.com` (or your FastAPI URL)
   - `MODEL_PATH`: `models/model.pkl`
   - `PYTHONUNBUFFERED`: `1`
5. Click "Create Web Service"

### Step 4: Configure Auto-Deploy

1. **In Render Dashboard:**
   - Go to each service
   - Enable "Auto-Deploy"
   - Select branch: `main` or `master`

2. **This ensures:**
   - Automatic deployment on code push
   - Automatic deployment after GitHub Actions completes

## 🔄 How to Trigger the Pipeline

### Method 1: Add New Data (Automatic)

1. **Add new data file:**
```bash
# Place your new data in data/new_data/latest.csv
cp your_new_data.csv data/new_data/latest.csv
```

2. **Commit and push:**
```bash
git add data/new_data/latest.csv
git commit -m "Add new training data"
git push origin main
```

3. **GitHub Actions automatically:**
   - Detects new data
   - Runs automated pipeline
   - Trains model
   - Sends email notification
   - Builds Docker images
   - Triggers Render deployment

### Method 2: Manual Trigger via GitHub Actions

1. **Go to GitHub Repository**
2. **Click "Actions" tab**
3. **Select "ML Model CI/CD Pipeline"**
4. **Click "Run workflow"**
5. **Check "Force model retraining"** (optional)
6. **Click "Run workflow"**

### Method 3: Code Changes

Any push to these paths triggers the pipeline:
- `data/salary_data.csv`
- `data/new_data/**`
- `src/**`
- `app.py`

```bash
# Example: Update training code
git add src/train_model.py
git commit -m "Update training parameters"
git push origin main
```

### Method 4: Force Retrain

```bash
# Create a dummy file to trigger retraining
touch data/new_data/trigger.txt
git add data/new_data/trigger.txt
git commit -m "Trigger model retraining"
git push origin main
```

## 📧 Email Notifications

### What You'll Receive

1. **Training Success Email:**
   - Model metrics (MAE, R², RMSE)
   - Training completion confirmation
   - Model file location

2. **Training Failure Email:**
   - Error details
   - Failure reason
   - Troubleshooting suggestions

3. **Drift Detection Email:**
   - Drift report
   - Feature comparison
   - Recommended actions

### Email Configuration

Ensure these GitHub Secrets are set:
- `SMTP_SERVER`
- `SMTP_PORT`
- `EMAIL_FROM`
- `EMAIL_PASSWORD`
- `EMAIL_TO`

## 🐳 Docker Images

### Building Locally

```bash
# FastAPI
docker build -t job-salary-api:latest .

# Streamlit
docker build -f Dockerfile.streamlit -t job-salary-streamlit:latest .
```

### Testing Locally

```bash
# FastAPI
docker run -p 8000:8000 job-salary-api:latest

# Streamlit
docker run -p 8501:8501 -e API_URL=http://localhost:8000 job-salary-streamlit:latest
```

## 🔍 Monitoring & Logs

### GitHub Actions Logs

1. Go to GitHub → Actions
2. Click on the latest workflow run
3. View logs for each step

### Render Logs

1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. View real-time logs

### Health Checks

- **FastAPI**: `https://your-api.onrender.com/health`
- **Streamlit**: `https://your-streamlit.onrender.com/_stcore/health`

## 🚨 Troubleshooting

### Pipeline Not Triggering

**Check:**
1. File is in correct path: `data/new_data/latest.csv`
2. File is committed and pushed
3. GitHub Actions is enabled
4. Workflow file is in `.github/workflows/`

### Build Failures

**Common Issues:**
1. **Missing dependencies**: Check `requirements.txt`
2. **Model not found**: Ensure model is trained first
3. **Docker build fails**: Check Dockerfile syntax

**Solution:**
```bash
# Test locally first
python automated_pipeline.py
docker build -t test .
```

### Deployment Failures

**Check:**
1. Render service logs
2. Environment variables are set
3. Health check path is correct
4. Port configuration matches

### Email Not Sending

**Check:**
1. GitHub Secrets are set correctly
2. SMTP credentials are valid
3. Test email manually: `python -m src.notify "Test" "Test"`

## 📊 Access Your Deployed Services

After deployment, you'll get URLs like:
- **FastAPI**: `https://job-salary-api.onrender.com`
- **FastAPI Docs**: `https://job-salary-api.onrender.com/docs`
- **Streamlit**: `https://job-salary-streamlit.onrender.com`

## ✅ Verification Checklist

- [ ] GitHub repository created and code pushed
- [ ] GitHub Secrets configured (email, Docker Hub)
- [ ] Render account created
- [ ] Services deployed on Render
- [ ] Auto-deploy enabled
- [ ] Test pipeline with new data
- [ ] Email notifications working
- [ ] Services accessible via URLs
- [ ] Health checks passing

## 🔄 Complete Workflow Example

```bash
# 1. Add new data
cp new_salary_data.csv data/new_data/latest.csv

# 2. Commit and push
git add data/new_data/latest.csv
git commit -m "Add new training data - trigger pipeline"
git push origin main

# 3. Monitor GitHub Actions
# Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/actions

# 4. Check email for notification

# 5. Verify deployment on Render
# Services will auto-update with new model
```

## 📝 Important Notes

1. **Model Persistence**: Models are stored in the container. For production, consider:
   - Using Render's persistent disk
   - Storing models in cloud storage (S3, etc.)
   - Using a database

2. **Data Storage**: For production, consider:
   - External database for data
   - Cloud storage for models
   - Backup strategy

3. **Scaling**: Render free tier has limitations:
   - Services sleep after inactivity
   - Limited resources
   - Consider paid plans for production

4. **Security**: 
   - Use environment variables for secrets
   - Enable HTTPS (automatic on Render)
   - Implement API authentication

## 🎯 Next Steps

1. **Set up monitoring**: Add logging and alerts
2. **Implement backups**: Regular model backups
3. **Add authentication**: Secure API endpoints
4. **Scale resources**: Upgrade Render plan if needed
5. **Set up CI/CD**: Already done! ✅

---

**Need Help?** Check:
- Render Docs: https://render.com/docs
- GitHub Actions Docs: https://docs.github.com/en/actions
- Project README for local development


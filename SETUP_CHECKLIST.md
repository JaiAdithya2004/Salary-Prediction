# ✅ Production Setup Checklist

Use this checklist to ensure everything is configured correctly for production deployment.

## 📋 Pre-Deployment Checklist

### 1. Code Preparation
- [ ] All code committed to GitHub
- [ ] Repository is public or Render has access
- [ ] `render.yaml` file exists
- [ ] Dockerfiles are production-ready
- [ ] `.dockerignore` is configured

### 2. GitHub Configuration
- [ ] Repository created on GitHub
- [ ] Code pushed to `main` or `master` branch
- [ ] GitHub Actions enabled
- [ ] Workflow files in `.github/workflows/`

### 3. GitHub Secrets (Required for Email)
- [ ] `SMTP_SERVER` - e.g., `smtp.gmail.com`
- [ ] `SMTP_PORT` - e.g., `587`
- [ ] `EMAIL_FROM` - Your email address
- [ ] `EMAIL_PASSWORD` - App password (not regular password)
- [ ] `EMAIL_TO` - Recipient email

### 4. GitHub Secrets (Optional - Docker Hub)
- [ ] `DOCKERHUB_USERNAME` - Your Docker Hub username
- [ ] `DOCKERHUB_TOKEN` - Docker Hub access token

### 5. Model Training
- [ ] Model trained locally: `python src/train_model.py`
- [ ] `models/model.pkl` exists
- [ ] `models/metrics.json` exists
- [ ] Model files committed to Git (or use persistent storage)

### 6. Email Configuration
- [ ] `.env` file created (for local testing)
- [ ] Gmail App Password generated (if using Gmail)
- [ ] Email test successful: `python -m src.notify "Test" "Test"`

## 🚀 Deployment Checklist

### 7. Render Account
- [ ] Render account created
- [ ] GitHub account connected
- [ ] Payment method added (for paid plans)

### 8. Render Deployment
- [ ] Blueprint created OR services created manually
- [ ] Services connected to GitHub repository
- [ ] Auto-deploy enabled
- [ ] Environment variables set
- [ ] Health check paths configured

### 9. Service Configuration

**FastAPI Service:**
- [ ] Name: `job-salary-api`
- [ ] Dockerfile: `./Dockerfile`
- [ ] Health Check: `/health`
- [ ] Port: `8000`
- [ ] Environment Variables:
  - [ ] `MODEL_PATH`: `models/model.pkl`
  - [ ] `PYTHONUNBUFFERED`: `1`

**Streamlit Service:**
- [ ] Name: `job-salary-streamlit`
- [ ] Dockerfile: `./Dockerfile.streamlit`
- [ ] Health Check: `/_stcore/health`
- [ ] Port: `8501`
- [ ] Environment Variables:
  - [ ] `API_URL`: FastAPI service URL
  - [ ] `MODEL_PATH`: `models/model.pkl`
  - [ ] `PYTHONUNBUFFERED`: `1`

## 🧪 Testing Checklist

### 10. Local Testing
- [ ] Pipeline runs: `python automated_pipeline.py`
- [ ] FastAPI works: `uvicorn app:app --reload`
- [ ] Streamlit works: `streamlit run streamlit_app.py`
- [ ] Docker builds: `docker build -t test .`
- [ ] Docker Compose works: `docker-compose up`

### 11. GitHub Actions Testing
- [ ] Workflow runs on push
- [ ] Pipeline executes successfully
- [ ] Email notifications received
- [ ] Docker images built
- [ ] Artifacts uploaded

### 12. Render Testing
- [ ] Services deploy successfully
- [ ] Health checks pass
- [ ] FastAPI accessible: `https://your-api.onrender.com/health`
- [ ] Streamlit accessible: `https://your-streamlit.onrender.com`
- [ ] API endpoints work
- [ ] Predictions work

## 🔄 Pipeline Testing

### 13. Trigger Pipeline
- [ ] Add new data: `data/new_data/latest.csv`
- [ ] Commit and push
- [ ] GitHub Actions triggered
- [ ] Pipeline completes successfully
- [ ] Email notification received
- [ ] Services redeployed

### 14. Manual Trigger
- [ ] GitHub Actions → Run workflow
- [ ] Force retrain option works
- [ ] Skip pipeline option works
- [ ] Workflow completes

## 📊 Monitoring Checklist

### 15. Logs & Monitoring
- [ ] GitHub Actions logs accessible
- [ ] Render logs accessible
- [ ] Email notifications working
- [ ] Health checks passing
- [ ] Services responding

### 16. Performance
- [ ] API response time acceptable
- [ ] Streamlit loads quickly
- [ ] Model predictions accurate
- [ ] No memory leaks
- [ ] Services stable

## 🔒 Security Checklist

### 17. Security
- [ ] Secrets stored in GitHub Secrets (not in code)
- [ ] `.env` file in `.gitignore`
- [ ] No hardcoded credentials
- [ ] HTTPS enabled (automatic on Render)
- [ ] API authentication (if needed)

## 📝 Documentation

### 18. Documentation
- [ ] `README_PRODUCTION.md` reviewed
- [ ] `PRODUCTION_DEPLOYMENT.md` reviewed
- [ ] `HOW_TO_TRIGGER_PIPELINE.md` reviewed
- [ ] Team members have access
- [ ] Deployment process documented

## ✅ Final Verification

### 19. End-to-End Test
- [ ] Add new data
- [ ] Pipeline runs automatically
- [ ] Model retrained
- [ ] Email received
- [ ] Services updated
- [ ] Predictions work with new model

### 20. Production Ready
- [ ] All checkboxes above completed
- [ ] Services running stable
- [ ] Monitoring in place
- [ ] Backup strategy defined
- [ ] Team trained on process

---

## 🎯 Quick Verification Commands

```bash
# Test pipeline locally
python automated_pipeline.py

# Test FastAPI
curl http://localhost:8000/health

# Test Streamlit
# Open http://localhost:8501

# Test email
python -m src.notify "Test" "Test"

# Build Docker
docker build -t test .

# Check GitHub Actions
# Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/actions

# Check Render
# Go to: https://dashboard.render.com
```

---

**Once all items are checked, your system is production-ready!** 🚀


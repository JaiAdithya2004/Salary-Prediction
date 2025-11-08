# 🔄 How to Trigger the Automated Pipeline

## Quick Reference

The automated pipeline runs: **Drift Detection → Preprocessing → Training → Evaluation → Notification → Docker Build → Deployment**

## 🎯 Methods to Trigger

### Method 1: Add New Data (Most Common) ⭐

**When to use:** When you have new training data

**Steps:**
1. Place new data in `data/new_data/latest.csv`
2. Commit and push:
```bash
git add data/new_data/latest.csv
git commit -m "Add new training data"
git push origin main
```

**What happens:**
- ✅ GitHub Actions detects new data
- ✅ Runs automated pipeline
- ✅ Trains new model
- ✅ Sends email notification
- ✅ Builds Docker images
- ✅ Deploys to Render

---

### Method 2: Manual Trigger via GitHub UI

**When to use:** When you want to retrain without new data

**Steps:**
1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`
2. Click "ML Model CI/CD Pipeline"
3. Click "Run workflow"
4. Options:
   - **Force retrain**: Check to retrain even without new data
   - **Skip pipeline**: Check to only build Docker (skip ML steps)
5. Click "Run workflow"

**What happens:**
- ✅ Workflow runs immediately
- ✅ Executes selected steps
- ✅ Sends notifications

---

### Method 3: Code Changes

**When to use:** When you update training code or model configuration

**Steps:**
```bash
# Example: Update training parameters
git add src/train_model.py
git commit -m "Update model hyperparameters"
git push origin main
```

**What happens:**
- ✅ GitHub Actions detects code change
- ✅ Runs pipeline with updated code
- ✅ Trains model with new settings
- ✅ Deploys updated version

---

### Method 4: Force Retrain (Empty Trigger)

**When to use:** When you want to retrain with existing data

**Steps:**
```bash
# Create a trigger file
touch data/new_data/trigger_$(date +%Y%m%d).txt
git add data/new_data/trigger_*.txt
git commit -m "Trigger model retraining"
git push origin main
```

**What happens:**
- ✅ Pipeline detects trigger file
- ✅ Retrains with existing data
- ✅ Updates model
- ✅ Deploys new version

---

## 📋 Pipeline Steps Breakdown

### Step 1: Drift Detection
- **What it does:** Compares new data with existing data
- **Output:** Drift report, email notification if drift detected
- **Time:** ~30 seconds

### Step 2: Data Preprocessing
- **What it does:** Cleans data, handles missing values, removes duplicates
- **Output:** Cleaned dataset
- **Time:** ~10 seconds

### Step 3: Data Merge
- **What it does:** Merges new data with existing dataset
- **Output:** Combined dataset
- **Time:** ~5 seconds

### Step 4: Model Training
- **What it does:** Trains Random Forest model
- **Output:** Trained model (`models/model.pkl`)
- **Time:** ~2-5 minutes

### Step 5: Model Evaluation
- **What it does:** Calculates MAE, R², RMSE
- **Output:** Metrics file (`models/metrics.json`)
- **Time:** ~10 seconds

### Step 6: Email Notification
- **What it does:** Sends email with results
- **Output:** Email sent to configured address
- **Time:** ~5 seconds

### Step 7: Docker Build
- **What it does:** Builds FastAPI and Streamlit images
- **Output:** Docker images
- **Time:** ~5-10 minutes

### Step 8: Deployment
- **What it does:** Deploys to Render (if configured)
- **Output:** Live services
- **Time:** ~5-10 minutes

**Total Time:** ~15-25 minutes

---

## 🔔 Email Notifications

### You'll Receive Emails For:

1. **Training Success:**
   - Subject: "✅ Model Retraining Completed Successfully"
   - Contains: Model metrics (MAE, R², RMSE)
   - Sent: After successful training

2. **Training Failure:**
   - Subject: "❌ Model Retraining Failed"
   - Contains: Error details
   - Sent: If training fails

3. **Drift Detected:**
   - Subject: "⚠️ Data Drift Detected"
   - Contains: Drift report, feature comparison
   - Sent: When drift is detected

---

## 🚨 Troubleshooting

### Pipeline Not Running?

**Check:**
1. ✅ File is in `data/new_data/latest.csv`
2. ✅ File is committed: `git status`
3. ✅ File is pushed: `git log`
4. ✅ GitHub Actions is enabled
5. ✅ Workflow file exists: `.github/workflows/deploy.yml`

**Debug:**
```bash
# Check if file exists
ls -la data/new_data/latest.csv

# Check git status
git status

# Check recent commits
git log --oneline -5
```

### Pipeline Failing?

**Common Issues:**

1. **Missing Model:**
   - Solution: Train model first locally
   ```bash
   python src/train_model.py
   git add models/model.pkl
   git commit -m "Add trained model"
   git push
   ```

2. **Email Configuration:**
   - Check GitHub Secrets are set
   - Test email: `python -m src.notify "Test" "Test"`

3. **Docker Build Fails:**
   - Test locally: `docker build -t test .`
   - Check Dockerfile syntax

---

## 📊 Monitoring Pipeline

### GitHub Actions

1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`
2. Click on latest workflow run
3. View logs for each step
4. Check for errors

### Email Notifications

- Check your inbox for notifications
- Check spam folder if not received
- Verify email in GitHub Secrets

### Render Dashboard

1. Go to: `https://dashboard.render.com`
2. Select your service
3. View "Events" tab for deployment history
4. View "Logs" tab for runtime logs

---

## ✅ Best Practices

1. **Before Pushing New Data:**
   - ✅ Validate data format
   - ✅ Check data quality
   - ✅ Test locally first

2. **After Pipeline Runs:**
   - ✅ Check email notification
   - ✅ Verify model metrics
   - ✅ Test deployed services
   - ✅ Check Render logs

3. **Regular Maintenance:**
   - ✅ Monitor model performance
   - ✅ Review drift reports
   - ✅ Update dependencies
   - ✅ Backup models

---

## 🎯 Quick Commands

```bash
# Trigger with new data
cp new_data.csv data/new_data/latest.csv
git add data/new_data/latest.csv
git commit -m "Add new data"
git push origin main

# Force retrain
touch data/new_data/trigger.txt
git add data/new_data/trigger.txt
git commit -m "Force retrain"
git push origin main

# Check pipeline status
# Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

---

**Need Help?** See `PRODUCTION_DEPLOYMENT.md` for detailed setup instructions.


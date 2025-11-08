"""
Streamlit App for Salary Prediction
Access the trained model through a user-friendly interface.
"""
import streamlit as st
import pandas as pd
import joblib
import os
import json
import requests
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Job Salary Predictor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
MODEL_PATH = "models/model.pkl"
METRICS_PATH = "models/metrics.json"
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .prediction-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    """Load the trained model."""
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            return model, None
        else:
            return None, f"Model file not found at {MODEL_PATH}. Please train the model first."
    except Exception as e:
        return None, f"Error loading model: {str(e)}"


@st.cache_data
def load_metrics():
    """Load model metrics."""
    try:
        if os.path.exists(METRICS_PATH):
            with open(METRICS_PATH, 'r') as f:
                return json.load(f)
        return None
    except:
        return None


def predict_with_model(model, input_data):
    """Make prediction using the loaded model."""
    try:
        prediction = model.predict(input_data)[0]
        return float(prediction), None
    except Exception as e:
        return None, f"Prediction error: {str(e)}"


def predict_with_api(input_data):
    """Make prediction using the FastAPI endpoint."""
    try:
        # Convert to API format
        api_data = {
            "Age": int(input_data["Age"].iloc[0]),
            "Gender": str(input_data["Gender"].iloc[0]),
            "Education_Level": str(input_data["Education Level"].iloc[0]),
            "Job_Title": str(input_data["Job Title"].iloc[0]),
            "Years_of_Experience": float(input_data["Years of Experience"].iloc[0])
        }
        
        response = requests.post(f"{API_URL}/predict", json=api_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result.get("predicted_salary"), None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API. Is the server running?"
    except Exception as e:
        return None, f"API Error: {str(e)}"


def main():
    """Main Streamlit app."""
    # Header
    st.markdown('<h1 class="main-header">💰 Job Salary Predictor</h1>', unsafe_allow_html=True)
    
    # Sidebar - Model Info
    with st.sidebar:
        st.header("📊 Model Information")
        
        # Load metrics
        metrics = load_metrics()
        if metrics:
            st.success("✅ Model Loaded")
            st.metric("MAE", f"${metrics.get('mae', 0):,.2f}")
            st.metric("R² Score", f"{metrics.get('r2', 0):.3f}")
            st.metric("RMSE", f"${metrics.get('rmse', 0):,.2f}")
        else:
            st.warning("⚠️ Metrics not available")
        
        st.divider()
        
        # Prediction mode
        st.header("⚙️ Settings")
        use_api = st.checkbox("Use FastAPI (if available)", value=False)
        
        if use_api:
            api_url = st.text_input("API URL", value=API_URL)
            st.info(f"Using API: {api_url}")
        else:
            st.info("Using local model")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["🔮 Predict Salary", "📊 Batch Prediction", "ℹ️ About"])
    
    with tab1:
        st.header("Single Salary Prediction")
        st.markdown("Enter employee details to predict their salary.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age", min_value=18, max_value=100, value=30, step=1)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            education = st.selectbox(
                "Education Level",
                ["High School", "Bachelor's", "Master's", "PhD"]
            )
        
        with col2:
            job_title = st.text_input("Job Title", value="Software Engineer")
            years_experience = st.number_input(
                "Years of Experience",
                min_value=0.0,
                max_value=50.0,
                value=5.0,
                step=0.5
            )
        
        # Predict button
        if st.button("🔮 Predict Salary", type="primary", use_container_width=True):
            # Prepare input data
            input_data = pd.DataFrame([{
                "Age": age,
                "Gender": gender,
                "Education Level": education,
                "Job Title": job_title,
                "Years of Experience": years_experience
            }])
            
            # Make prediction
            with st.spinner("Predicting salary..."):
                if use_api:
                    prediction, error = predict_with_api(input_data)
                else:
                    model, model_error = load_model()
                    if model_error:
                        prediction, error = None, model_error
                    else:
                        prediction, error = predict_with_model(model, input_data)
            
            # Display result
            if error:
                st.error(f"❌ {error}")
            elif prediction:
                st.markdown(f"""
                    <div class="prediction-box">
                        <h2>Predicted Salary</h2>
                        <h1>${prediction:,.2f}</h1>
                    </div>
                """, unsafe_allow_html=True)
                
                # Show input summary
                with st.expander("📋 Input Summary"):
                    st.json({
                        "Age": age,
                        "Gender": gender,
                        "Education Level": education,
                        "Job Title": job_title,
                        "Years of Experience": years_experience
                    })
    
    with tab2:
        st.header("Batch Salary Prediction")
        st.markdown("Upload a CSV file with employee data to predict salaries for multiple employees.")
        
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ Loaded {len(df)} records")
                
                # Check required columns
                required_cols = ["Age", "Gender", "Education Level", "Job Title", "Years of Experience"]
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                    st.info(f"Required columns: {', '.join(required_cols)}")
                else:
                    if st.button("🔮 Predict All Salaries", type="primary"):
                        with st.spinner("Predicting salaries..."):
                            if use_api:
                                # Use API for batch prediction
                                try:
                                    api_data = []
                                    for _, row in df.iterrows():
                                        api_data.append({
                                            "Age": int(row["Age"]),
                                            "Gender": str(row["Gender"]),
                                            "Education_Level": str(row["Education Level"]),
                                            "Job_Title": str(row["Job Title"]),
                                            "Years_of_Experience": float(row["Years of Experience"])
                                        })
                                    
                                    response = requests.post(
                                        f"{API_URL}/predict/batch",
                                        json=api_data,
                                        timeout=30
                                    )
                                    
                                    if response.status_code == 200:
                                        results = response.json()
                                        predictions = [p["predicted_salary"] for p in results["predictions"]]
                                        df["Predicted Salary"] = predictions
                                        st.success("✅ Predictions completed!")
                                    else:
                                        st.error(f"API Error: {response.status_code}")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                            else:
                                # Use local model
                                model, model_error = load_model()
                                if model_error:
                                    st.error(f"❌ {model_error}")
                                else:
                                    predictions = model.predict(df[required_cols])
                                    df["Predicted Salary"] = predictions
                                    st.success("✅ Predictions completed!")
                        
                        # Display results
                        if "Predicted Salary" in df.columns:
                            st.dataframe(df, use_container_width=True)
                            
                            # Download button
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results",
                                data=csv,
                                file_name="salary_predictions.csv",
                                mime="text/csv"
                            )
                            
                            # Summary statistics
                            st.subheader("📊 Summary Statistics")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Employees", len(df))
                            with col2:
                                st.metric("Average Salary", f"${df['Predicted Salary'].mean():,.2f}")
                            with col3:
                                st.metric("Total Salary", f"${df['Predicted Salary'].sum():,.2f}")
            
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
    
    with tab3:
        st.header("About This Application")
        st.markdown("""
        ### Job Salary Predictor
        
        This application uses a machine learning model to predict employee salaries based on:
        - **Age**: Employee's age
        - **Gender**: Employee's gender
        - **Education Level**: Highest level of education
        - **Job Title**: Current job position
        - **Years of Experience**: Years of professional experience
        
        ### Model Information
        - **Algorithm**: Random Forest Regressor
        - **Training Data**: Historical salary data
        - **Features**: 5 input features
        - **Output**: Predicted annual salary
        
        ### How to Use
        1. **Single Prediction**: Enter employee details and click "Predict Salary"
        2. **Batch Prediction**: Upload a CSV file with employee data
        3. **API Mode**: Enable to use FastAPI backend (if running)
        
        ### Technical Details
        - Built with Streamlit
        - Model trained using scikit-learn
        - FastAPI backend available
        - Dockerized for easy deployment
        """)
        
        # Model metrics
        metrics = load_metrics()
        if metrics:
            st.subheader("Model Performance")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mean Absolute Error", f"${metrics.get('mae', 0):,.2f}")
            with col2:
                st.metric("R² Score", f"{metrics.get('r2', 0):.3f}")
            with col3:
                st.metric("RMSE", f"${metrics.get('rmse', 0):,.2f}")


if __name__ == "__main__":
    main()


"""FastAPI application for salary prediction API."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import joblib
import pandas as pd
import os
import numpy as np

app = FastAPI(
    title="Job Salary Predictor API",
    description="ML-powered API for predicting job salaries based on employee features",
    version="1.0.0"
)

# Global model variable
model = None
MODEL_PATH = "models/model.pkl"


class SalaryPredictionRequest(BaseModel):
    """Request model for salary prediction."""
    Age: int = Field(..., ge=18, le=100, description="Employee age")
    Gender: str = Field(..., description="Employee gender")
    Education_Level: str = Field(..., description="Education level")
    Job_Title: str = Field(..., description="Job title")
    Years_of_Experience: float = Field(..., ge=0, le=50, description="Years of experience")


class SalaryPredictionResponse(BaseModel):
    """Response model for salary prediction."""
    predicted_salary: float
    confidence: Optional[str] = None


def load_model():
    """Load the trained model from disk."""
    global model
    if model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH}. Please train the model first."
            )
        model = joblib.load(MODEL_PATH)
        print(f"✅ Model loaded from {MODEL_PATH}")
    return model


@app.on_event("startup")
async def startup_event():
    """Load model on application startup."""
    try:
        load_model()
    except FileNotFoundError as e:
        print(f"⚠️ Warning: {e}")
        print("   API will still start, but predictions will fail until model is trained.")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Job Salary Predictor API",
        "status": "running",
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    model_loaded = model is not None or os.path.exists(MODEL_PATH)
    return {
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded
    }


@app.post("/predict", response_model=SalaryPredictionResponse)
async def predict_salary(request: SalaryPredictionRequest):
    """
    Predict salary based on employee features.
    
    Args:
        request: SalaryPredictionRequest with employee features
    
    Returns:
        SalaryPredictionResponse with predicted salary
    """
    if model is None:
        try:
            load_model()
        except FileNotFoundError:
            raise HTTPException(
                status_code=503,
                detail="Model not available. Please train the model first."
            )
    
    try:
        # Convert request to DataFrame with correct column names
        # Handle both snake_case and space-separated column names
        input_data = pd.DataFrame([{
            "Age": request.Age,
            "Gender": request.Gender,
            "Education Level": request.Education_Level,
            "Job Title": request.Job_Title,
            "Years of Experience": request.Years_of_Experience
        }])
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        
        return SalaryPredictionResponse(
            predicted_salary=float(prediction),
            confidence="high"  # Could be enhanced with prediction intervals
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


@app.post("/predict/batch")
async def predict_salary_batch(requests: List[SalaryPredictionRequest]):
    """
    Predict salaries for multiple employees in batch.
    
    Args:
        requests: List of SalaryPredictionRequest objects
    
    Returns:
        List of predictions
    """
    if model is None:
        try:
            load_model()
        except FileNotFoundError:
            raise HTTPException(
                status_code=503,
                detail="Model not available. Please train the model first."
            )
    
    try:
        # Convert requests to DataFrame
        input_data = pd.DataFrame([{
            "Age": req.Age,
            "Gender": req.Gender,
            "Education Level": req.Education_Level,
            "Job Title": req.Job_Title,
            "Years of Experience": req.Years_of_Experience
        } for req in requests])
        
        # Make predictions
        predictions = model.predict(input_data)
        
        return {
            "predictions": [
                {
                    "predicted_salary": float(pred),
                    "input": req.dict()
                }
                for pred, req in zip(predictions, requests)
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


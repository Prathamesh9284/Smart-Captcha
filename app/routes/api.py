import time
import json
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import BehaviorDetectionResponse, VisitInfoResponse
from app.services.behavior_detection_service import BehaviorDetectionService
from app.repositories.firebase_repository import FirebaseRepository

router = APIRouter(prefix="/api", tags=["bot-detection"])

behavior_service = BehaviorDetectionService()
firebase_repo = FirebaseRepository()

@router.get("/", response_model=dict)
async def root():
    """Root endpoint to check if the API is running"""
    return {"message": "Bot Detection API is running"}


@router.post("/predict_behavior", response_model=BehaviorDetectionResponse)
async def predict_behavior(
    mouse_file: UploadFile = File(...),
    key_file: UploadFile = File(...),
    browser_info: str = Form(...),
    fingerprint: str = Form(...)
):
    """
    Predict if user behavior indicates bot activity
    
    Args:
        mouse_file: CSV file with mouse movement data
        key_file: CSV file with keyboard typing data
        browser_info: JSON string with browser details
        fingerprint: Unique browser fingerprint
        
    Returns:
        Detection results for different behavior aspects
    """
    try:
        # Read uploaded files
        mouse_data = await mouse_file.read()
        key_data = await key_file.read()
        
        # Parse browser info
        browser_info_dict = json.loads(browser_info)
        
        # Analyze behavior
        results = await behavior_service.analyze_behavior(
            mouse_data, 
            key_data, 
            browser_info_dict, 
            fingerprint
        )
        
        return BehaviorDetectionResponse(**results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.post("/add_visit_info", response_model=VisitInfoResponse)
async def add_visit_info(
    fingerprint: str = Form(...),
    timestamp: int = Form(None)
):
    """
    Record user visit information
    
    Args:
        fingerprint: Unique browser fingerprint
        timestamp: Visit timestamp (optional)
        
    Returns:
        Confirmation of saved information
    """
    try:
        # Use provided timestamp or create a new one
        current_timestamp = timestamp or int(time.time() * 1000)
        
        # Save visit info
        result = await firebase_repo.save_fingerprint_visit(fingerprint, current_timestamp)
        
        return VisitInfoResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving visit info: {str(e)}")
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class BrowserInfo(BaseModel):
    """Browser information schema"""
    userAgent: str
    webdriver: bool
    platform: str
    screenResolution: str
    maxTouchPoints: int
    pluginsCount: Optional[int] = None
    languages: Optional[List[str]] = None


class BehaviorDetectionResponse(BaseModel):
    """Response schema for behavior detection"""
    mouse_result: str
    key_result: str
    is_automated: str
    is_bot: str


class VisitInfo(BaseModel):
    """Visit information schema"""
    fingerprint: str
    timestamp: int


class VisitInfoResponse(BaseModel):
    """Response schema for visit info"""
    message: str
    timestamp: int
    fingerprint: str
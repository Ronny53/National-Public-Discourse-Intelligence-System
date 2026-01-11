from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from backend.config.settings import get_settings
from backend.email.email_service import get_email_service
from backend.database.alert_history import alert_history
from backend.database.database import get_db
from backend.database.services import DatabaseService

router = APIRouter()
settings = get_settings()

# Initialize alert history cooldown from settings
alert_history.set_cooldown(settings.ALERT_COOLDOWN_MINUTES)


@router.get("/status")
async def get_alert_status(db: Session = Depends(get_db)):
    """
    Get current alert status including risk score and alert history.
    Admin-only endpoint (enforced by frontend).
    """
    db_service = DatabaseService(db)
    latest_summary = db_service.get_latest_dashboard_summary()
    
    if not latest_summary:
        return {
            "risk_score": 0.0,
            "risk_level": "Low",
            "alert_status": "Normal",
            "auto_alerts_enabled": True,
            "threshold": settings.ALERT_THRESHOLD,
            "last_alert_time": None,
            "can_send_alert": True,
            "time_until_next_alert": None
        }
    
    risk_score = latest_summary.escalation_risk_score
    risk_level = latest_summary.escalation_risk_level
    
    # Determine alert status
    if risk_score >= settings.ALERT_THRESHOLD:
        alert_status = "High Risk"
    else:
        alert_status = "Normal"
    
    last_alert_time = alert_history.get_last_alert_time()
    can_send = alert_history.can_send_alert()
    time_until_next = alert_history.get_time_until_next_alert()
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "alert_status": alert_status,
        "auto_alerts_enabled": True,  # Can be made configurable later
        "threshold": settings.ALERT_THRESHOLD,
        "last_alert_time": last_alert_time.isoformat() if last_alert_time else None,
        "can_send_alert": can_send,
        "time_until_next_alert": time_until_next.total_seconds() if time_until_next else None
    }


@router.post("/send-manual")
async def send_manual_alert(db: Session = Depends(get_db)):
    """
    Manually send an alert email.
    Admin-only endpoint (enforced by frontend).
    """
    # Check cooldown
    if not alert_history.can_send_alert():
        time_until = alert_history.get_time_until_next_alert()
        minutes_remaining = int(time_until.total_seconds() / 60) if time_until else 0
        raise HTTPException(
            status_code=429,
            detail=f"Alert cooldown active. Please wait {minutes_remaining} more minutes."
        )
    
    # Get current risk score
    db_service = DatabaseService(db)
    latest_summary = db_service.get_latest_dashboard_summary()
    
    if not latest_summary:
        risk_score = 0.0
    else:
        risk_score = latest_summary.escalation_risk_score
    
    # Send email
    email_service = get_email_service()
    success = email_service.send_alert(risk_score, is_manual=True)
    
    if success:
        alert_history.record_alert()
        return {
            "status": "sent",
            "message": "Alert email sent successfully",
            "risk_score": risk_score,
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send alert email. Please check email configuration."
        )


@router.post("/test-email")
async def test_email():
    """
    Send a test email to verify email configuration.
    Admin-only endpoint (enforced by frontend).
    """
    email_service = get_email_service()
    success = email_service.send_test_email()
    
    if success:
        return {
            "status": "sent",
            "message": "Test email sent successfully"
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send test email. Please check email configuration."
        )


@router.get("/config")
async def get_alert_config():
    """
    Get alert configuration (threshold, cooldown, etc.).
    Admin-only endpoint (enforced by frontend).
    """
    return {
        "threshold": settings.ALERT_THRESHOLD,
        "cooldown_minutes": settings.ALERT_COOLDOWN_MINUTES,
        "email_configured": bool(
            settings.EMAIL_HOST and 
            settings.EMAIL_USER and 
            settings.EMAIL_APP_PASSWORD and 
            settings.EMAIL_RECIPIENTS
        ),
        "recipients": settings.EMAIL_RECIPIENTS
    }

"""SMS service for phone verification."""

from typing import Optional

from ..core.config import get_settings
from ..core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class SMSService:
    """Service for sending SMS messages."""
    
    def __init__(self) -> None:
        self.client = None
        self._setup_client()
    
    def _setup_client(self) -> None:
        """Set up Twilio client if credentials are configured."""
        try:
            if settings.twilio_account_sid and settings.twilio_auth_token:
                from twilio.rest import Client
                self.client = Client(
                    settings.twilio_account_sid,
                    settings.twilio_auth_token
                )
                logger.info("Twilio SMS client initialized")
            else:
                logger.info("SMS service not configured (missing Twilio credentials)")
        except ImportError:
            logger.warning("Twilio not installed - SMS service unavailable")
        except Exception as e:
            logger.error("Error setting up SMS client", error=str(e))
    
    async def send_verification_code(self, phone_number: str, code: str) -> bool:
        """Send SMS verification code."""
        if not self.client:
            logger.warning("SMS client not available", phone_number=phone_number)
            return False
        
        try:
            message_body = f"""
Your Neighborhood Sharing Platform verification code is: {code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this message.
            """.strip()
            
            message = self.client.messages.create(
                body=message_body,
                from_=settings.twilio_phone_number,
                to=phone_number
            )
            
            logger.info(
                "SMS verification code sent",
                phone_number=phone_number,
                message_sid=message.sid
            )
            return True
            
        except Exception as e:
            logger.error(
                "Error sending SMS verification code",
                phone_number=phone_number,
                error=str(e)
            )
            return False
    
    async def send_notification(
        self,
        phone_number: str,
        message: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Send SMS notification."""
        if not self.client:
            logger.warning("SMS client not available", phone_number=phone_number)
            return False
        
        try:
            sms_message = self.client.messages.create(
                body=message,
                from_=settings.twilio_phone_number,
                to=phone_number
            )
            
            logger.info(
                "SMS notification sent",
                phone_number=phone_number,
                user_id=user_id,
                message_sid=sms_message.sid
            )
            return True
            
        except Exception as e:
            logger.error(
                "Error sending SMS notification",
                phone_number=phone_number,
                user_id=user_id,
                error=str(e)
            )
            return False
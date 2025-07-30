from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship
from database.session import Base
from security.encryption import encrypt_field, decrypt_field
from datetime import datetime, timedelta
import random
import string
from loguru import logger

class UserAccess(Base):
    __tablename__ = 'user_access'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(20), unique=True, nullable=False)
    telegram_username = Column(String(50))
    access_level = Column(String(10), default='basic')  # basic, premium, admin
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)
    is_approved = Column(Boolean, default=False)
    captcha_token = Column(String(10))
    captcha_expiry = Column(DateTime)
    
    # Encrypted contact information
    _contact_email = Column('contact_email', String(255))
    
    @property
    def contact_email(self):
        return decrypt_field(self._contact_email) if self._contact_email else None
    
    @contact_email.setter
    def contact_email(self, value):
        self._contact_email = encrypt_field(value)
    
    def generate_captcha(self):
        """Generate CAPTCHA for user registration"""
        self.captcha_token = ''.join(random.choices(string.digits, k=6))
        self.captcha_expiry = datetime.utcnow() + timedelta(minutes=10)
        return self.captcha_token
    
    def verify_captcha(self, token: str) -> bool:
        """Verify CAPTCHA token"""
        if datetime.utcnow() > self.captcha_expiry:
            return False
        return token == self.captcha_token

def register_user(session, telegram_id: int, username: str) -> UserAccess:
    """Register a new user with CAPTCHA verification"""
    user = session.query(UserAccess).filter_by(telegram_id=str(telegram_id)).first()
    
    if user:
        if not user.is_approved:
            return user  # Return existing unapproved user
        raise ValueError("User already registered")
    
    user = UserAccess(
        telegram_id=str(telegram_id),
        telegram_username=username
    )
    captcha = user.generate_captcha()
    
    session.add(user)
    session.commit()
    logger.info(f"New user registered: {telegram_id}")
    return user, captcha

def approve_user(session, telegram_id: int, access_level: str = 'basic'):
    """Approve user access (admin function)"""
    user = session.query(UserAccess).filter_by(telegram_id=str(telegram_id)).first()
    if not user:
        raise ValueError("User not found")
    
    user.is_approved = True
    user.access_level = access_level
    session.commit()
    return user

def is_user_approved(telegram_id: int) -> bool:
    """Check if user is approved"""
    session = get_session()
    user = session.query(UserAccess).filter_by(telegram_id=str(telegram_id)).first()
    return user and user.is_approved
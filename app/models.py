from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    custom_alias = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    clicks_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)

    clicks = relationship("ClickAnalytics", back_populates="url", cascade="all, delete-orphan")

class ClickAnalytics(Base):
    __tablename__ = "click_analytics"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id", ondelete="CASCADE"), nullable=False)
    short_code = Column(String, index=True, nullable=False)
    clicked_at = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    referer = Column(String, nullable=True)

    url = relationship("URL", back_populates="clicks")

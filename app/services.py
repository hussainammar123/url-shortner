from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from .models import URL, ClickAnalytics
from .cache import CacheService
from .utils import generate_short_code, is_valid_url

class URLService:
    @staticmethod
    def create_short_url(
        db: Session,
        original_url: str,
        custom_alias: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> URL:
        if not is_valid_url(original_url):
            raise ValueError("Invalid URL scheme or format. Must begin with http:// or https://")

        if custom_alias:
            alias = custom_alias.strip()
            existing_alias = db.query(URL).filter(
                (URL.custom_alias == alias) | (URL.short_code == alias)
            ).first()
            if existing_alias:
                raise ValueError("Custom alias already in use.")
            short_code = alias
        else:
            # Generate unique short code
            while True:
                short_code = generate_short_code()
                existing = db.query(URL).filter(URL.short_code == short_code).first()
                if not existing:
                    break

        db_url = URL(
            original_url=original_url,
            short_code=short_code,
            custom_alias=custom_alias,
            expires_at=expires_at
        )
        db.add(db_url)
        db.commit()
        db.refresh(db_url)

        # Cache in Redis
        CacheService.set_url(short_code, original_url)

        return db_url

    @staticmethod
    def get_original_url(db: Session, short_code: str) -> Optional[str]:
        # 1. Try Redis cache first
        cached_url = CacheService.get_url(short_code)
        if cached_url:
            return cached_url

        # 2. Database lookup
        db_url = db.query(URL).filter(
            (URL.short_code == short_code) | (URL.custom_alias == short_code),
            URL.is_active == True
        ).first()

        if not db_url:
            return None

        # Check expiration
        if db_url.expires_at and db_url.expires_at < datetime.utcnow():
            return None

        # Warm Redis cache
        CacheService.set_url(short_code, db_url.original_url)
        return db_url.original_url

    @staticmethod
    def record_click(
        db: Session,
        short_code: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        referer: Optional[str] = None
    ):
        db_url = db.query(URL).filter(
            (URL.short_code == short_code) | (URL.custom_alias == short_code)
        ).first()

        if db_url:
            db_url.clicks_count += 1
            analytics = ClickAnalytics(
                url_id=db_url.id,
                short_code=short_code,
                user_agent=user_agent,
                ip_address=ip_address,
                referer=referer
            )
            db.add(analytics)
            db.commit()

            CacheService.increment_click(short_code)

    @staticmethod
    def get_recent_urls(db: Session, limit: int = 10) -> List[URL]:
        return db.query(URL).order_by(URL.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_system_stats(db: Session) -> Dict[str, Any]:
        total_urls = db.query(URL).count()
        total_clicks = db.query(ClickAnalytics).count()
        recent_urls = URLService.get_recent_urls(db, limit=5)
        
        return {
            "total_urls": total_urls,
            "total_clicks": total_clicks,
            "recent_urls": recent_urls
        }

    @staticmethod
    def get_url_stats(db: Session, short_code: str) -> Optional[Dict[str, Any]]:
        db_url = db.query(URL).filter(
            (URL.short_code == short_code) | (URL.custom_alias == short_code)
        ).first()
        
        if not db_url:
            return None

        clicks = db.query(ClickAnalytics).filter(
            ClickAnalytics.url_id == db_url.id
        ).order_by(ClickAnalytics.clicked_at.desc()).limit(20).all()

        return {
            "id": db_url.id,
            "original_url": db_url.original_url,
            "short_code": db_url.short_code,
            "custom_alias": db_url.custom_alias,
            "created_at": db_url.created_at.isoformat(),
            "clicks_count": db_url.clicks_count,
            "recent_clicks": [
                {
                    "clicked_at": c.clicked_at.isoformat(),
                    "user_agent": c.user_agent,
                    "referer": c.referer
                }
                for c in clicks
            ]
        }

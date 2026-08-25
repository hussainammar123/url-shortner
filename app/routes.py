from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, BackgroundTasks, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from .database import get_db
from .services import URLService
from .utils import generate_qr_code_png

router = APIRouter()

class ShortenRequest(BaseModel):
    url: str
    custom_alias: Optional[str] = None
    expires_in_days: Optional[int] = None

class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    qr_code_url: str
    created_at: str

@router.post("/api/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
def create_short_url(
    payload: ShortenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    expires_at = None
    if payload.expires_in_days and payload.expires_in_days > 0:
        expires_at = datetime.utcnow() + timedelta(days=payload.expires_in_days)

    try:
        url_obj = URLService.create_short_url(
            db=db,
            original_url=payload.url,
            custom_alias=payload.custom_alias,
            expires_at=expires_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    base_url = str(request.base_url).rstrip("/")
    short_url = f"{base_url}/{url_obj.short_code}"
    qr_code_url = f"{base_url}/api/qr/{url_obj.short_code}"

    return ShortenResponse(
        short_code=url_obj.short_code,
        short_url=short_url,
        original_url=url_obj.original_url,
        qr_code_url=qr_code_url,
        created_at=url_obj.created_at.isoformat()
    )

@router.get("/api/urls")
def get_urls(limit: int = 10, request: Request = None, db: Session = Depends(get_db)):
    base_url = str(request.base_url).rstrip("/") if request else ""
    urls = URLService.get_recent_urls(db, limit=limit)
    return [
        {
            "id": u.id,
            "short_code": u.short_code,
            "short_url": f"{base_url}/{u.short_code}",
            "original_url": u.original_url,
            "clicks_count": u.clicks_count,
            "created_at": u.created_at.isoformat(),
            "qr_code_url": f"{base_url}/api/qr/{u.short_code}"
        }
        for u in urls
    ]

@router.get("/api/stats")
def get_system_stats(db: Session = Depends(get_db)):
    return URLService.get_system_stats(db)

@router.get("/api/stats/{short_code}")
def get_url_stats(short_code: str, db: Session = Depends(get_db)):
    stats = URLService.get_url_stats(db, short_code)
    if not stats:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return stats

@router.get("/api/qr/{short_code}")
def get_qr_code(short_code: str, request: Request):
    base_url = str(request.base_url).rstrip("/")
    target_short_url = f"{base_url}/{short_code}"
    png_bytes = generate_qr_code_png(target_short_url)
    return Response(content=png_bytes, media_type="image/png")

@router.get("/{short_code}")
def redirect_to_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Ignore requests for favicon or system paths
    if short_code in ("favicon.ico", "robots.txt", "static", "api"):
        raise HTTPException(status_code=404, detail="Not found")

    original_url = URLService.get_original_url(db, short_code)
    if not original_url:
        raise HTTPException(status_code=404, detail="Short URL not found or expired")

    # Record analytics in background
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    referer = request.headers.get("referer")
    
    background_tasks.add_task(
        URLService.record_click,
        db,
        short_code,
        user_agent,
        ip_address,
        referer
    )

    return RedirectResponse(url=original_url, status_code=307)

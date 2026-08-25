import io
import string
import secrets
from urllib.parse import urlparse
import qrcode

BASE62_ALPHABET = string.ascii_letters + string.digits

def generate_short_code(length: int = 6) -> str:
    """Generates a random base62 string of specified length."""
    return "".join(secrets.choice(BASE62_ALPHABET) for _ in range(length))

def is_valid_url(url: str) -> bool:
    """Validates if a string is a properly formatted URL with http/https scheme."""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False

def generate_qr_code_png(data: str) -> bytes:
    """Generates a high-resolution PNG image of a QR code containing the data string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#00285d", back_color="#ffffff")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

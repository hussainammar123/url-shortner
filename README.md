# SwiftLink - High-Performance URL Shortener

![SwiftLink Architecture](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi)
![Database](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)
![Cache](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis)
![Proxy](https://img.shields.io/badge/Nginx-Alpine-009639?style=flat-square&logo=nginx)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)

**SwiftLink** is a production-ready, ultra-fast URL Shortener service built with FastAPI, PostgreSQL, Redis caching, and Nginx. It includes an interactive modern UI designed with Stitch, dynamic QR code generation, real-time analytics tracking, and custom alias support.

---

## 📁 Project Directory Structure

```
url-shortener/
├── app/
│   ├── main.py          # FastAPI application entry point & middleware
│   ├── routes.py        # API endpoints & redirection router
│   ├── models.py        # SQLAlchemy models (URL, ClickAnalytics)
│   ├── database.py      # Database session & engine initialization
│   ├── cache.py         # Redis caching layer with in-memory fallback
│   ├── services.py      # Business logic (URL creation, redirection, stats)
│   ├── utils.py         # Base62 generator, URL validator, QR code generator
│   └── static/
│       └── index.html   # Integrated interactive Stitch UI frontend
├── Dockerfile           # Python 3.11-slim container build configuration
├── docker-compose.yml   # Orchestration for FastAPI, PostgreSQL, Redis & Nginx
├── requirements.txt     # Python dependencies
├── nginx.conf           # Nginx reverse proxy configuration
└── README.md            # Comprehensive project documentation
```

---

## ✨ Features

- **⚡ Lightning-Fast Redirection**: Powered by Redis caching for $O(1)$ lookup performance.
- **🎨 Stitch Modern UI**: Responsive dark theme UI with custom aliases, instant copy buttons, and activity charts.
- **📱 Automated QR Codes**: PNG QR code images generated automatically for every shortened link.
- **📊 Real-time Click Analytics**: Track total click counts, timestamps, user-agents, and referrers.
- **🛠 Flexible Custom Slugs**: Create branded custom aliases or generate standard 6-character short codes.
- **🛡 Fallback Resilience**: Auto-switches to SQLite and in-memory cache when running outside Docker or without Redis.

---

## 🛠 Tech Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11)
- **Database**: [PostgreSQL](https://www.postgresql.org/) (via SQLAlchemy ORM)
- **Cache**: [Redis](https://redis.io/)
- **Reverse Proxy**: [Nginx](https://www.nginx.com/)
- **Containerization**: [Docker & Docker Compose](https://www.docker.com/)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript (integrated from Stitch design)

---

## 🚀 Quick Start Guide

### Option 1: Running with Docker Compose (Recommended)

1. Ensure Docker Desktop is installed and running.
2. Navigate to the `url-shortener` directory:
   ```bash
   cd url-shortener
   ```
3. Start the entire container stack:
   ```bash
   docker-compose up --build -d
   ```
4. Access the application in your browser:
   - **Frontend UI & Short URLs**: [http://localhost](http://localhost) (Nginx port 80)
   - **FastAPI OpenAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

To stop the containers:
```bash
docker-compose down
```

---

### Option 2: Running Locally Without Docker (Standalone Dev Mode)

1. Navigate to `url-shortener`:
   ```bash
   cd url-shortener
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
5. Open [http://localhost:8000](http://localhost:8000) in your web browser. (The app will automatically use SQLite database and in-memory fallback cache).

---

## 📡 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/shorten` | Shortens a URL (accepts `url`, `custom_alias`, `expires_in_days`). |
| `GET` | `/{short_code}` | Redirects to original long URL & records click analytics. |
| `GET` | `/api/urls` | Lists recent shortened URLs for UI dashboard. |
| `GET` | `/api/stats` | System-wide statistics (total URLs, total clicks). |
| `GET` | `/api/stats/{short_code}` | Detailed analytics for a specific short code. |
| `GET` | `/api/qr/{short_code}` | Generates PNG QR code image for a short URL. |

---

## 💻 Example cURL Commands

### 1. Shorten a URL
```bash
curl -X POST "http://localhost:8000/api/shorten" \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://github.com",
           "custom_alias": "my-github"
         }'
```

*Response:*
```json
{
  "short_code": "my-github",
  "short_url": "http://localhost:8000/my-github",
  "original_url": "https://github.com",
  "qr_code_url": "http://localhost:8000/api/qr/my-github",
  "created_at": "2026-08-05T14:30:00.000000"
}
```

### 2. Access Short URL (Redirect)
```bash
curl -i "http://localhost:8000/my-github"
```

### 3. Fetch Click Statistics
```bash
curl "http://localhost:8000/api/stats/my-github"
```

---

## ⚙️ Environment Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./url_shortener.db` | Database connection string. |
| `REDIS_HOST` | `redis` | Redis server hostname. |
| `REDIS_PORT` | `6379` | Redis server port. |
| `REDIS_URL` | `redis://redis:6379/0` | Full Redis connection string. |

---

## 📄 License

MIT License. Designed and developed with FastAPI and Stitch.

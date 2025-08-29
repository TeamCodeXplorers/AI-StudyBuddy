# 🤖 AI StudyBuddy

AI-powered study assistant using Google Gemini.

## 🚀 Quick Start

1. Clone repo
2. `python -m venv venv && venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. Set `GOOGLE_API_KEY` in `.env`
5. `python app.py`

## 🌐 Deploy to Render

1. Push to GitHub
2. On Render: New → Web Service → Connect repo
3. Environment: Python
4. Build: `pip install -r requirements.txt`
5. Start: `gunicorn app:app`
6. Add env vars: `GOOGLE_API_KEY` and `SECRET_KEY`

## 🔐 Features

- AI chat with Gemini
- User auth (signup/login)
- Secure password hashing
- SQLite database

## 📁 Files

- `app.py` - Main Flask app
- `templates/` - HTML pages
- `static/style.css` - Styling
- `requirements.txt` - Dependencies

"""WSGI entry point for production deployment."""

import os

from dotenv import load_dotenv

load_dotenv()

from app import app

if __name__ == "__main__":
    app.run(host=os.getenv("FLASK_HOST", "127.0.0.1"), port=int(os.getenv("FLASK_PORT", "5000")))

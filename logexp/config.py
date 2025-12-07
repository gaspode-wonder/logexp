import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///logexp.db"  # fallback if env not set
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

"""
config/settings.py
------------------
All application configuration is loaded here from the .env file.

Why Pydantic BaseSettings?
──────────────────────────
• Reads environment variables automatically — no manual os.getenv() calls.
• Validates types at startup — a missing required variable (like MONGO_URI)
  crashes immediately with a clear error instead of failing silently later.
• Single source of truth for every config value in the app.

Why environment variables?
──────────────────────────
Hardcoding a MongoDB URI or any secret in source code is dangerous:
  1. The secret gets committed to Git → anyone with repo access can see it.
  2. You can't change it per-environment (dev / staging / prod) without
     editing code.
Environment variables solve both: they live outside the codebase,
are different per machine, and are never committed.
"""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_DEFAULT_JWT_KEY = "super-secret-jwt-signing-key-dev-changelog-widget"


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────────
    app_name: str = "Changelog Widget"
    app_version: str = "1.0.0"
    environment: str = "development"  # "development" | "staging" | "production"

    # ── CORS ──────────────────────────────────────────────────────────────────
    frontend_url: str = "http://localhost:5173"
    cors_origins: str = ""  # Optional comma-separated additional origins

    # ── MongoDB (Step 2) ──────────────────────────────────────────────────────
    # MONGO_URI must be set in .env — no default so the app fails fast
    # if it's missing rather than connecting to the wrong database.
    mongo_uri: str
    database_name: str = "changelog_db"

    # ── JWT & Authentication (Step 4) ─────────────────────────────────────────
    jwt_secret_key: str = DEV_DEFAULT_JWT_KEY
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    email_verification_token_expire_hours: int = 24
    password_reset_token_expire_hours: int = 1
    cookie_secure: bool = False  # Enforced True in production
    cookie_samesite: str = "lax"

    # ── Admin Bootstrap ───────────────────────────────────────────────────────
    # Comma-separated list of emails that are granted ADMIN role in production
    admin_emails: str = ""

    # ── File Uploads (Step 14) ────────────────────────────────────────────────
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 5

    # Read from .env file in the current working directory
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        is_prod = self.environment.lower() == "production"
        if is_prod:
            # Enforce non-default, high-entropy JWT secret key in production
            if self.jwt_secret_key == DEV_DEFAULT_JWT_KEY:
                raise ValueError(
                    "CRITICAL SECURITY CONFIGURATION ERROR: "
                    "Cannot use the default development JWT_SECRET_KEY in production! "
                    "Please set a strong, random secret key (at least 32 characters) in .env"
                )
            if len(self.jwt_secret_key) < 32:
                raise ValueError(
                    "JWT_SECRET_KEY must be at least 32 characters long in production."
                )
            # Enforce HTTPS-only secure cookies in production
            self.cookie_secure = True
        return self

    def get_admin_emails(self) -> list[str]:
        """Returns parsed, lowercased list of admin email addresses."""
        if not self.admin_emails:
            return []
        return [email.strip().lower() for email in self.admin_emails.split(",") if email.strip()]

    def get_cors_origins(self) -> list[str]:
        """
        Returns authorized CORS origins based on environment.
        In production: strictly the configured frontend_url and explicit cors_origins.
        In development: allows frontend_url and standard localhost / 127.0.0.1 variants.
        """
        origins = set()
        if self.frontend_url:
            origins.add(self.frontend_url.rstrip("/"))

        if self.cors_origins:
            for o in self.cors_origins.split(","):
                clean = o.strip().rstrip("/")
                if clean:
                    origins.add(clean)

        if self.environment.lower() == "development":
            origins.add("http://localhost:5173")
            origins.add("http://127.0.0.1:5173")
            origins.add("http://localhost:3000")

        return list(origins)


# Module-level singleton — import `settings` wherever config is needed.
# FastAPI starts once; this is evaluated once at import time.
settings = Settings()

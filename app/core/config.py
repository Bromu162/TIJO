from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///./parking.db"
    grace_period_minutes: int = 15
    app_title: str = "Paid Parking Management System"
    app_version: str = "1.0.0"


settings = Settings()

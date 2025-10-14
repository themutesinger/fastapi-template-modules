from .settings import Settings

# Eagerly instantiate settings for convenient imports like `from configs import settings`.
settings = Settings()

__all__ = ["Settings", "settings"]

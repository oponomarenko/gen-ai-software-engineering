import os


class Settings:
    """Application configuration sourced from environment variables."""

    app_name: str = "Intelligent Customer Support System"
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]
    max_import_file_size_bytes: int = int(
        os.getenv("MAX_IMPORT_FILE_SIZE_BYTES", str(5 * 1024 * 1024))
    )


settings = Settings()

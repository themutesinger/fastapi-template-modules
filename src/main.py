from presentations.api.app import app

if __name__ == "__main__":
    # For local development: python -m src.main or python src/main.py
    import uvicorn

    uvicorn.run("presentations.api.app:app", host="0.0.0.0", port=8000, reload=True)

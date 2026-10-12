"""
NutriScore - Web Application Runner
Launches the FastAPI backend and serves the interactive frontend at http://localhost:8000
"""

import sys
import webbrowser
import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print("🥗 Starting NutriScore AI Web Application...")
    print("🎨 Theme: Vanilla Cream & Rosewood Botanical Aesthetic")
    print("⚡ Endpoints: http://127.0.0.1:8000")
    print("=" * 65)

    # Open browser automatically after a short delay
    try:
        webbrowser.open("http://127.0.0.1:8000")
    except Exception:
        pass

    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)

"""
ShadeRoute AI — Quick Start
Run this file from Anaconda Prompt to start the backend.
"""
import uvicorn, os, sys

if __name__ == "__main__":
    print()
    print("=" * 52)
    print("  ShadeRoute AI — Smart Shadow Navigation")
    print("  Bengaluru  12.9716°N  77.5946°E")
    print("=" * 52)
    print("  Backend API  :  http://localhost:8000")
    print("  API Docs     :  http://localhost:8000/docs")
    print("  Frontend UI  :  http://localhost:8000/ui")
    print("=" * 52)
    print("  Open browser → http://localhost:8000/docs")
    print("  Press Ctrl+C to stop the server")
    print()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

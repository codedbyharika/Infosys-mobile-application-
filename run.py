"""
EcoAir Intelligence — Production Web Application & API Launcher
Runs FastAPI ASGI server hosting the modern SPA dashboard and ML microservice.
"""

import sys
import os
import uvicorn

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")

    print("=" * 72)
    print("  [EcoAir Intelligence] Environmental AI Platform")
    print("=" * 72)
    print(f"  * Local Web Dashboard:   http://127.0.0.1:{port}/")
    print(f"  * Android Emulator Host: http://10.0.2.2:{port}/")
    print(f"  * Interactive API Docs:  http://127.0.0.1:{port}/docs")
    print(f"  * Stations Telemetry:    http://127.0.0.1:{port}/api/stations")
    print("=" * 72)
    print("  Press Ctrl+C to stop the server.")
    print("=" * 72)

    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()

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
    host = os.environ.get("HOST", "127.0.0.1")

    print("=" * 72)
    print("  [EcoAir Intelligence] Environmental AI Platform")
    print("=" * 72)
    print(f"  * Web Dashboard:       http://{host}:{port}/")
    print(f"  * Interactive API Docs: http://{host}:{port}/docs")
    print(f"  * Stations Telemetry:   http://{host}:{port}/api/stations")
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

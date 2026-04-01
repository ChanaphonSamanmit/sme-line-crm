import os, sys, pathlib

def handler(request):
    root = pathlib.Path(__file__).parent.parent
    result = {
        "cwd": os.getcwd(),
        "root": str(root),
        "static_exists": (root / "static").exists(),
        "static_admin_exists": (root / "static" / "admin").exists(),
        "root_files": sorted(os.listdir(root)),
        "python": sys.version,
    }
    try:
        import app.config
        result["config_ok"] = True
    except Exception as e:
        result["config_error"] = str(e)
    try:
        import app.main
        result["app_ok"] = True
    except Exception as e:
        result["app_error"] = str(e)

    from http.server import BaseHTTPRequestHandler
    import json

    class Response:
        def __init__(self):
            self.status_code = 200
            self.body = json.dumps(result, indent=2)
            self.headers = {"Content-Type": "application/json"}

    return Response()

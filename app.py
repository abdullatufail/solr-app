from pathlib import Path
import os

import requests
from flask import Flask, Response, request, send_file


BASE_DIR = Path(__file__).resolve().parent
SOLR_BASE = os.environ.get("SOLR_BASE", "").strip().rstrip("/")

app = Flask(__name__, static_folder=None)


def _frontend_file() -> Path | None:
    candidates = [
        BASE_DIR / "index.html",
        BASE_DIR / "students.html",
        BASE_DIR / "solr-9.6.0" / "server" / "solr-webapp" / "webapp" / "students.html",
    ]
    for file_path in candidates:
        if file_path.exists():
            return file_path
    return None


@app.get("/")
def home() -> Response:
    frontend = _frontend_file()
    if frontend is None:
        return Response("No frontend file found. Put index.html in this folder.", status=404)
    return send_file(frontend)


@app.get("/students.html")
def students_page() -> Response:
    return home()


@app.route("/solr/<path:solr_path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def solr_proxy(solr_path: str) -> Response:
    proxy_headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length", "connection"}
    }

    candidate_bases: list[str] = []
    if SOLR_BASE:
        candidate_bases.append(SOLR_BASE)
    else:
        candidate_bases.extend(
            [
                "http://127.0.0.1:8983/solr",
                "http://localhost:8983/solr",
            ]
        )
        if request.remote_addr:
            candidate_bases.append(f"http://{request.remote_addr}:8983/solr")

    last_error: requests.exceptions.RequestException | None = None
    for base in candidate_bases:
        target_url = f"{base}/{solr_path}"
        try:
            upstream = requests.request(
                method=request.method,
                url=target_url,
                params=request.args,
                data=request.get_data(),
                headers=proxy_headers,
                timeout=30,
            )
            excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}
            response_headers = [(k, v) for k, v in upstream.headers.items() if k.lower() not in excluded]
            return Response(upstream.content, status=upstream.status_code, headers=response_headers)
        except requests.exceptions.RequestException as exc:
            last_error = exc

    return Response(
        f"Cannot reach Solr. Tried: {', '.join(candidate_bases)}. Last error: {last_error}",
        status=502,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

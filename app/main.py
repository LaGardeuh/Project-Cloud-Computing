import os
import time
import json
import yaml
from flask import Flask, jsonify, render_template_string
from azure.storage.blob import BlobServiceClient

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)


# --- Cache mémoire simple avec TTL ---
_cache = {}
CACHE_TTL = 60  # secondes


def get_cached(key, loader_fn):
    now = time.time()
    if key in _cache and (now - _cache[key]["ts"]) < CACHE_TTL:
        return _cache[key]["data"]
    data = loader_fn()
    _cache[key] = {"data": data, "ts": now}
    return data


# --- Lecture Azure Blob Storage ---
def load_blob(filename):
    conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    container = os.environ.get("AZURE_CONTAINER_NAME", "content")

    # Mode local : si pas de connexion Azure, on lit un fichier local
    if not conn_str:
        local_path = os.path.join(os.path.dirname(__file__), "mock_data", filename)
        with open(local_path, "r") as f:
            if filename.endswith(".yaml"):
                return yaml.safe_load(f)
            return json.load(f)

    client = BlobServiceClient.from_connection_string(conn_str)
    blob = client.get_container_client(container).download_blob(filename)
    content = blob.readall().decode("utf-8")
    if filename.endswith(".yaml"):
        return yaml.safe_load(content)
    return json.loads(content)


# --- Endpoints API ---
@app.route("/api/events")
def events():
    logger.info("GET /api/events")
    data = get_cached("events", lambda: load_blob("events.json"))
    return jsonify({"items": data})


@app.route("/api/news")
def news():
    logger.info("GET /api/news")
    data = get_cached("news", lambda: load_blob("news.json"))
    return jsonify({"items": data})


@app.route("/api/faq")
def faq():
    logger.info("GET /api/faq")
    data = get_cached("faq", lambda: load_blob("faq.yaml"))
    return jsonify({"items": data})


# --- Health checks ---
@app.route("/healthz")
def healthz():
    return jsonify({"status": "healthy"}), 200


@app.route("/readyz")
def readyz():
    return jsonify({"status": "ready"}), 200


# --- Interface web minimale ---
@app.route("/")
def index():
    return render_template_string("""
    <!DOCTYPE html><html><head><title>Content Platform</title>
    <style>body{font-family:sans-serif;max-width:700px;margin:40px auto;padding:0 20px}
    a{display:inline-block;margin:8px;padding:10px 18px;background:#4f46e5;color:white;
    border-radius:6px;text-decoration:none}h1{color:#1e1b4b}</style></head>
    <body><h1>Content Platform</h1>
    <p>Endpoints disponibles :</p>
    <a href="/api/events">/api/events</a>
    <a href="/api/news">/api/news</a>
    <a href="/api/faq">/api/faq</a>
    <a href="/healthz">/healthz</a>
    <a href="/readyz">/readyz</a>
    </body></html>
    """)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

#!/usr/bin/env python3
"""
Run this once before a Locust sweep (or whenever you reseed data).
Fetches all article documentIds and saves them to document_ids.json,
so locustfile.py can just read from disk instead of hitting the API
itself at test-start (which was causing a thundering-herd problem
when every simulated user fetched this independently).
"""

import json
import sys
import requests

STRAPI_URL = "http://127.0.0.1:1337"

resp = requests.get(f"{STRAPI_URL}/api/articles?pagination[pageSize]=100")
if resp.status_code != 200:
    print(f"Failed to fetch articles: {resp.status_code} {resp.text}")
    sys.exit(1)

data = resp.json().get("data") or []
ids = [item["documentId"] for item in data]

if not ids:
    print("Warning: got zero documentIds. Is the Article table actually seeded?")

with open("document_ids.json", "w") as f:
    json.dump(ids, f)

print(f"Saved {len(ids)} documentIds to document_ids.json")

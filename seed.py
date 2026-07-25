import requests

STRAPI_URL = "http://127.0.0.1:1337"
API_TOKEN = "99a2c6039eca21ca6dfcbfeb9b89c6fa211de4fafb5d16382f1872384fdddc5da0fde6e3a71acd92f08974da53845f34a06860377ebe2a4a4ec0b8d0bd5cc8819e50cabfd433c293370a25dd7870518ec7d0e95aa90eb0d8648060432d136d150195f052df7e73f8323f5f2883feba02692db16ef5609c7f07efb5500b6c9a9f"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

resp = requests.get(
    f"{STRAPI_URL}/api/articles?pagination[pageSize]=100", headers=headers
)
articles = resp.json()["data"]
print(f"fetched {len(articles)} articles")

for i, article in enumerate(articles):
    doc_id = article["documentId"]
    payload = {
        "data": {
            "body": f"Sample body for load testing purposes, entry {i} \n" * 20,
        }
    }

    resp = requests.put(
        f"{STRAPI_URL}/api/articles/{doc_id}", json=payload, headers=headers
    )
    if resp.status_code not in (200, 201):
        print(f"Failed at {i}: {resp.status_code}; {resp.text}")

print("Done.")

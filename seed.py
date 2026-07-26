import requests

STRAPI_URL = "https://cms-strapi-4vy8.onrender.com"
API_TOKEN = "3679ad6d7de6e052271e02b28bc5090b137f758e9d3485702b8e0aefe78640d1166a8637f865e03cc7f319a3ae55dae6c1ece8beb74f30549a861d461ebd82a0f1a18543f18fc49cb27cdb4c9ca5c5ff7f1bd4fa8412ce3e3f415edf5349bd652be2ee569a0de233c6cc39d7eb3e48c09133c3eeeeb7dbc059536d3b7f882400"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

sample_titles = [
    "Notes on load testing",
    "System Design Basics",
    "Postgres tuning",
    "Caching Strategies",
]

created = 0
for i in range(100):
    payload = {
        "data": {
            "Title": f"{sample_titles[i % len(sample_titles)]} #{i}",
            "body": f"Sample body for load testing, entry {i}. \n" * 20,
            "Author": f"Author #{i % 100 + 1}",
        }
    }

    resp = requests.post(f"{STRAPI_URL}/api/articles", json=payload, headers=headers)
    if resp.status_code not in {200, 201}:
        print(f"Failed at {i}: {resp.status_code}; {resp.text}")
    else:
        created += 1

print(f"created {created}/100 articles")
# resp = requests.get(
#     f"{STRAPI_URL}/api/articles?pagination[pageSize]=100", headers=headers
# )
# articles = resp.json()["data"]
# print(f"fetched {len(articles)} articles")
#
# for i, article in enumerate(articles):
#     doc_id = article["documentId"]
#     payload = {
#         "data": {
#             "body": f"Sample body for load testing purposes, entry {i} \n" * 20,
#         }
#     }
#
#     resp = requests.put(
#         f"{STRAPI_URL}/api/articles/{doc_id}", json=payload, headers=headers
#     )
#     if resp.status_code not in (200, 201):
#         print(f"Failed at {i}: {resp.status_code}; {resp.text}")
#
print("Done.")

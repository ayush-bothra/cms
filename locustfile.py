import random
import json
from pathlib import Path
from locust import HttpUser, task, between

_ids_path = Path("document_ids.json")
if _ids_path.exists():
    with open(_ids_path) as f:
        DOCUMENT_IDS = json.load(f)
else:
    DOCUMENT_IDS = []
    print(
        "WARNING: document_ids.json not found, please run fetch_ids.py first, "
        "get_single_article will get skipped"
    )


class StrapiHeader(HttpUser):
    wait_time = between(1, 2)

    @task(5)
    def list_articles(self):
        page = random.randint(1, 5)
        self.client.get(
            f"/api/articles?pagination[page]={page}&pagination[pageSize]=10",
            name="/api/articles [list]",
        )

    @task(3)
    def list_articles_populated(self):
        page = random.randint(1, 5)
        self.client.get(
            f"/api/articles?populate=*&pagination[page]={page}&pagination[pageSize]=10",
            name="/api/articles [populated]",
        )

    @task(1)
    def get_single_article(self):
        if not DOCUMENT_IDS:
            return
        doc_id = random.choice(DOCUMENT_IDS)
        self.client.get(
            f"/api/articles/{doc_id}",
            name="/api/articles/[documentId]",
        )

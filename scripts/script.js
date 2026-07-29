import http from "k6/http";
import { check, sleep } from "k6";

const TARGET_VUS = __ENV.VUS ? parseInt(__ENV.VUS) : 100;
const SPAWN_RATE = __ENV.SPAWN_RATE ? parseInt(__ENV.SPAWN_RATE) : 5;
const TOTAL_SECONDS = __ENV.TOTAL_SECONDS ? parseInt(__ENV.TOTAL_SECONDS) : 120;
const rampUpSeconds = Math.ceil(TOTAL_SECONDS / SPAWN_RATE);
const holdSeconds = Math.max(TOTAL_SECONDS - rampUpSeconds, 0);

export const options = {
  scenarios: {
    sweep: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: `${rampUpSeconds}s`, target: TARGET_VUS },
        { duration: `${holdSeconds}s`, target: TARGET_VUS },
      ],
      gracefulRampDown: "0s",
    },
  },
};

const BASE_URL = __ENV.BASE_URL || "http://strapi:1337";

let DOCUMENT_IDS = [];
try {
  DOCUMENT_IDS = JSON.parse(open("./document_ids.json"));
} catch (e) {
  console.warn(
    "document_ids.json not found, get_single_article will be skipped",
  );
}

function listArticles() {
  const page = Math.floor(Math.random() * 5) + 1;

  const res = http.get(
    `${BASE_URL}/api/articles?pagination[page]=${page}&pagination[pageSize]=10`,
    { tags: { name: "/api/articles [list]", load_level: String(TARGET_VUS) } },
  );

  check(res, { "list_articles status is 200": (r) => r.status === 200 });
}

function listArticlesPopulated() {
  const page = Math.floor(Math.random() * 5) + 1;
  const res = http.get(
    `${BASE_URL}/api/articles?populate=*&pagination[page]=${page}&pagination[pageSize]=10`,
    {
      tags: {
        name: "/api/articles [populated]",
        load_level: String(TARGET_VUS),
      },
    },
  );
  check(res, {
    "list_articles_populated status is 200": (r) => r.status === 200,
  });
}

function getSingleArticle() {
  if (DOCUMENT_IDS.length === 0) {
    return;
  }
  const docId = DOCUMENT_IDS[Math.floor(Math.random() * DOCUMENT_IDS.length)];
  const res = http.get(`${BASE_URL}/api/articles/${docId}`, {
    tags: {
      name: "/api/articles [documentId]",
      load_level: String(TARGET_VUS),
    },
  });

  check(res, { "get_single_article status is 200": (r) => r.status === 200 });
}

export default function runLoadTests() {
  const roll = Math.random() * 9;
  if (roll < 5) {
    listArticles();
  } else if (roll < 8) {
    listArticlesPopulated();
  } else {
    getSingleArticle();
  }
  sleep(Math.random() + 1);
}

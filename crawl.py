import csv
import requests
import time

KEYWORDS = ["history", "literature", "terrorism"]
PAGES_PER_KEYWORD = 3
OUTPUT_FILE = "books_seed.csv"

headers = {
    "User-Agent": "BookSeeder/1.0 (danghuulong394@gmail.com)"
}

rows = []
seen = set()

for keyword in KEYWORDS:
    for page in range(1, PAGES_PER_KEYWORD + 1):
        url = "https://openlibrary.org/search.json"
        params = {"q": keyword, "page": page}

        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        for doc in data.get("docs", []):
            title = doc.get("title")
            authors = "; ".join(doc.get("author_name", [])) if doc.get("author_name") else ""
            isbn = doc.get("isbn", [None])[0] if doc.get("isbn") else ""
            key = doc.get("key", "")

            dedupe_key = (title, authors, isbn or key)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            cover_i = doc.get("cover_i")
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg" if cover_i else ""

            rows.append({
                "title": title or "",
                "author": authors,
                "publisher": "; ".join(doc.get("publisher", [])[:3]) if doc.get("publisher") else "",
                "first_publish_year": doc.get("first_publish_year", ""),
                "isbn": isbn,
                "language": "; ".join(doc.get("language", [])) if doc.get("language") else "",
                "subject": "; ".join(doc.get("subject", [])[:5]) if doc.get("subject") else "",
                "openlibrary_key": key,
                "cover_url": cover_url
            })

        time.sleep(1)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "title", "author", "publisher", "first_publish_year",
        "isbn", "language", "subject", "openlibrary_key", "cover_url"
    ])
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {len(rows)} rows to {OUTPUT_FILE}")
import mimetypes
import uuid
from urllib.parse import urlparse

import requests
from django.conf import settings


def infer_supabase_url_from_database_url(db_url: str) -> str:
    host = urlparse(db_url).hostname or ""
    if host.startswith("db.") and host.endswith(".supabase.co"):
        project_ref = host[len("db."): -len(".supabase.co")]
        return f"https://{project_ref}.supabase.co"
    raise ValueError("DATABASE_URL không đúng định dạng Supabase.")


def get_supabase_url() -> str:
    if getattr(settings, "SUPABASE_URL", None):
        return settings.SUPABASE_URL
    db_url = settings.DATABASES["default"].get("HOST")  # đôi khi không có
    # an toàn hơn: lấy từ env
    import os
    return infer_supabase_url_from_database_url(os.getenv("DATABASE_URL", ""))


def build_public_url(bucket: str, path: str) -> str:
    supabase_url = get_supabase_url()
    return f"{supabase_url}/storage/v1/object/public/{bucket}/{path}"


def upload_to_supabase(
    file_obj,
    *,
    original_name: str,
    folder: str = "ebooks",
    ebook_id: int | None = None,
    entity_id: int | None = None,
) -> dict:
    _id = ebook_id if ebook_id is not None else entity_id
    if _id is None:
        raise TypeError("upload_to_supabase cần ebook_id hoặc entity_id")

    bucket = getattr(settings, "SUPABASE_STORAGE_BUCKET", "ebooks")
    key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", None)
    if not key:
        raise RuntimeError("Thiếu SUPABASE_SERVICE_ROLE_KEY")

    ext = (original_name.split(".")[-1] if "." in original_name else "bin").lower()
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    path = f"{folder}/{_id}/{safe_name}"

    mime, _ = mimetypes.guess_type(original_name)
    mime = mime or "application/octet-stream"

    supabase_url = get_supabase_url()
    endpoint = f"{supabase_url}/storage/v1/object/{bucket}/{path}"

    file_obj.seek(0)
    data = file_obj.read()

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": mime,
        "x-upsert": "true",
    }

    r = requests.post(endpoint, headers=headers, data=data, timeout=60)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Upload failed: {r.status_code} {r.text}")

    return {"path": path, "public_url": build_public_url(bucket, path), "mime": mime}
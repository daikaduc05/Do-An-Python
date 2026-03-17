import csv
import os
from io import BytesIO
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.ebooks.models import Author, Category, Ebook
from apps.ebooks.supabase_storage_http import upload_to_supabase


class Command(BaseCommand):
    help = "Import ebooks from Open Library CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **options):
        csv_path = options["csv_path"]

        default_category, _ = Category.objects.get_or_create(
            name="Imported Books",
            defaults={"slug": "imported-books"}
        )

        created_count = 0
        skipped_count = 0

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    with transaction.atomic():
                        title = (row.get("title") or "").strip()
                        if not title:
                            skipped_count += 1
                            self.stdout.write(self.style.WARNING("Skip row without title"))
                            continue

                        author_raw = (row.get("author") or "").strip()
                        author_name = author_raw.split(";")[0].strip() if author_raw else "Unknown Author"

                        author, _ = Author.objects.get_or_create(name=author_name)

                        subject_raw = (row.get("subject") or "").strip()
                        category = default_category
                        if subject_raw:
                            first_subject = subject_raw.split(";")[0].strip()
                            if first_subject:
                                category, _ = Category.objects.get_or_create(
                                    name=first_subject[:100],
                                    defaults={"slug": slugify(first_subject)[:100] or "uncategorized"}
                                )

                        description = (
                            f"Imported from Open Library. "
                            f"First publish year: {row.get('first_publish_year') or 'Unknown'}. "
                            f"Open Library key: {row.get('openlibrary_key') or ''}"
                        )

                        ebook, created = Ebook.objects.get_or_create(
                            title=title,
                            author=author,
                            defaults={
                                "description": description,
                                "price": 100,
                                "category": category,
                                "is_active": True,
                            }
                        )

                        if not created:
                            skipped_count += 1
                            self.stdout.write(self.style.WARNING(f"Skip existing: {title}"))
                            continue

                        cover_source_url = (row.get("cover_url") or "").strip()
                        if cover_source_url:
                            try:
                                resp = requests.get(cover_source_url, timeout=30)
                                resp.raise_for_status()

                                parsed = urlparse(cover_source_url)
                                filename = os.path.basename(parsed.path) or f"cover_{ebook.id}.jpg"

                                file_obj = BytesIO(resp.content)
                                file_obj.name = filename

                                result = upload_to_supabase(
                                    file_obj,
                                    folder="covers",
                                    ebook_id=ebook.id,
                                    original_name=filename,
                                )
                                ebook.cover_url = result["public_url"]
                                ebook.cover_mime = result["mime"]
                                ebook.save(update_fields=["cover_url", "cover_mime"])
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f"Cover upload failed for {title}: {e}"))

                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f"Imported: {title}"))

                except Exception as e:
                    skipped_count += 1
                    self.stdout.write(self.style.ERROR(f"Error row {row.get('title')}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created={created_count}, Skipped={skipped_count}"
        ))
from django.db import migrations
from django.utils.text import slugify

def unique_slug(Category, base):
    base = (base or "category")[:100]
    if not Category.objects.filter(slug=base).exists():
        return base
    i = 2
    while True:
        s = f"{base}-{i}"[:100]
        if not Category.objects.filter(slug=s).exists():
            return s
        i += 1

def forwards(apps, schema_editor):
    Ebook = apps.get_model("ebooks", "Ebook")
    Category = apps.get_model("ebooks", "Category")

    for e in Ebook.objects.all():
        raw = (getattr(e, "category", "") or "").strip()
        if not raw:
            continue

        cat = Category.objects.filter(name__iexact=raw).first()
        if not cat:
            cat = Category.objects.create(
                name=raw,
                slug=unique_slug(Category, slugify(raw)),
                description="",
            )

        e.category_fk_id = cat.id
        e.save(update_fields=["category_fk"])

class Migration(migrations.Migration):
    dependencies = [
        ("ebooks", "0008_create_categories_table"),  # ✅ đổi nếu migration cuối của bạn khác
    ]
    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
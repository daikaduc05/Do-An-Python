from django.db import migrations

def create_categories_if_missing(apps, schema_editor):
    schema_editor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id bigserial PRIMARY KEY,
        name varchar(100) UNIQUE NOT NULL,
        slug varchar(100) UNIQUE NOT NULL,
        description text NOT NULL DEFAULT '',
        created_at timestamptz NOT NULL DEFAULT now()
    );
    """)

class Migration(migrations.Migration):
    dependencies = [
        ("ebooks", "0007_ebook_category_fk_alter_ebook_category"),
    ]
    operations = [
        migrations.RunPython(create_categories_if_missing, migrations.RunPython.noop),
    ]
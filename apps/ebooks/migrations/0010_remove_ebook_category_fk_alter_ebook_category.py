from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ebooks", "0009_migrate_category_text_to_fk"),
    ]

    operations = [
        # 1) drop text field "category" (CharField)
        migrations.RemoveField(
            model_name="ebook",
            name="category",
        ),

        # 2) rename FK field "category_fk" -> "category"
        migrations.RenameField(
            model_name="ebook",
            old_name="category_fk",
            new_name="category",
        ),
    ]
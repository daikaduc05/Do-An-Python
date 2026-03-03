from django import forms
from django.contrib import admin
from .models import Author, Category, Ebook
from .supabase_storage_http import upload_to_supabase  # file bạn tạo theo hướng HTTP
from django.contrib import messages

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class EbookAdminForm(forms.ModelForm):
    ebook_file = forms.FileField(required=False, help_text="Upload file sách (PDF/EPUB) lên Supabase Storage")
    cover_file = forms.ImageField(required=False, help_text="Upload ảnh bìa lên Supabase Storage")

    class Meta:
        model = Ebook
        fields = "__all__"


@admin.register(Ebook)
class EbookAdmin(admin.ModelAdmin):
    form = EbookAdminForm
    list_display = ['title', 'author', 'category', 'price', 'is_active', 'created_at']
    search_fields = ['title', 'author__name']
    list_filter = ['category', 'is_active', 'created_at']
    readonly_fields = ['created_at']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        uploaded = form.cleaned_data.get("ebook_file")
        if uploaded:
            try:
                result = upload_to_supabase(uploaded, folder="ebooks", ebook_id=obj.id, original_name=uploaded.name)
                obj.file_url = result["public_url"]
                obj.file_mime = result["mime"]
                obj.save(update_fields=["file_url", "file_mime"])
                messages.success(request, "✅ Upload file sách lên Supabase thành công.")
            except Exception as e:
                messages.error(request, f"❌ Upload Supabase thất bại (file sách): {e}")

        cover = form.cleaned_data.get("cover_file")
        if cover:
            try:
                result = upload_to_supabase(cover, folder="covers", ebook_id=obj.id, original_name=cover.name)
                obj.cover_url = result["public_url"]
                obj.cover_mime = result["mime"]
                obj.save(update_fields=["cover_url", "cover_mime"])
                messages.success(request, "✅ Upload ảnh bìa lên Supabase thành công.")
            except Exception as e:
                messages.error(request, f"❌ Upload Supabase thất bại (ảnh bìa): {e}")
from django import forms
from django.contrib import admin
from .models import Ebook, Author, Category, EbookReview, EbookReviewImage
from .supabase_storage_http import upload_to_supabase  # file bạn tạo theo hướng HTTP
from django.contrib import messages
from django.utils.html import format_html

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
    list_display = ['cover_preview', 'title', 'author', 'category', 'price', 'is_active', 'created_at']
    search_fields = ['title', 'author__name']
    list_filter = ['category', 'is_active', 'created_at']
    readonly_fields = ['created_at', 'file_url', 'file_mime', 'cover_url', 'cover_mime']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("author", "category")

    def cover_preview(self, obj):
        if getattr(obj, "cover_url", None):
            return format_html('<img src="{}" style="height:60px;border-radius:6px;" />', obj.cover_url)
        return "-"
    cover_preview.short_description = "Cover"

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

class EbookReviewImageInline(admin.TabularInline):
    model = EbookReviewImage
    extra = 0


@admin.register(EbookReview)
class EbookReviewAdmin(admin.ModelAdmin):
    list_display = ['ebook', 'user', 'rating', 'created_at', 'updated_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['ebook__title', 'user__email', 'content']
    autocomplete_fields = ['ebook', 'user']
    inlines = [EbookReviewImageInline]


@admin.register(EbookReviewImage)
class EbookReviewImageAdmin(admin.ModelAdmin):
    list_display = ['review', 'created_at']
    autocomplete_fields = ['review']
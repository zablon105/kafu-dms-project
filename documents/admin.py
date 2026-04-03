from django.contrib import admin
from .models import Document, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "uploaded_by", "visibility", "category", "created_at")
    list_filter = ("visibility", "category")
    search_fields = ("title",)
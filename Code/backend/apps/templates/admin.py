from django.contrib import admin

from .models import DesktopTemplate


@admin.register(DesktopTemplate)
class DesktopTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "enabled", "updated_at")
    list_filter = ("enabled",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

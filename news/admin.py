from django.contrib import admin
from .models import Headline


@admin.register(Headline)
class HeadlineAdmin(admin.ModelAdmin):
    list_display = ('title_short', 'category', 'language', 'leaning', 'created_at')
    list_filter = ('category', 'language', 'leaning', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'img', 'url')
        }),
        ('Classification', {
            'fields': ('category', 'language', 'leaning')
        }),
        ('Metadata', {
            'fields': ('date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def title_short(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'

# radio_app/admin.py
from django.contrib import admin
from .models import (
    Frequency, News, Program, LiveStream, Member,
    ContactMessage, SocialMedia, SiteSetting, AdBanner
)

@admin.register(Frequency)
class FrequencyAdmin(admin.ModelAdmin):
    list_display = ['frequency', 'get_location_display', 'is_active', 'order']
    list_filter = ['is_active', 'location']
    search_fields = ['location', 'custom_location', 'slogan']
    list_editable = ['is_active', 'order']

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'is_featured', 'publish_date']
    list_filter = ['is_published', 'is_featured', 'category', 'publish_date']
    search_fields = ['title', 'content', 'author']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'publish_date'

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'host', 'start_time', 'end_time', 'days', 'is_active']
    list_filter = ['is_active', 'is_live', 'days']
    search_fields = ['title', 'description', 'host']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(LiveStream)
class LiveStreamAdmin(admin.ModelAdmin):
    list_display = ['name', 'stream_type', 'bitrate', 'is_active']
    list_editable = ['is_active']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['created_at', 'updated_at', 'ip_address', 'user_agent']

@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ['platform', 'display_name', 'url', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active', 'platform']

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only one instance allowed
        return not SiteSetting.objects.exists()

@admin.register(AdBanner)
class AdBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'is_active', 'start_date', 'end_date']
    list_filter = ['is_active', 'position', 'start_date']
    search_fields = ['title', 'url']

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']
# radio_app/admin.py
from django.contrib import admin
from .models import (
    Frequency, News, Program, ProgramSchedule, LiveStream, Member,
    ContactMessage, SocialMedia, SiteSetting, AdBanner, PageVisit
)


class ProgramScheduleInline(admin.TabularInline):
    """Lets you add several air-time slots (e.g. 06:00-06:20 AND 07:00-07:30)
    for the same program without duplicating the program itself."""
    model = ProgramSchedule
    extra = 1
    fields = ['days', 'start_time', 'end_time', 'is_live', 'order']
    ordering = ['order', 'start_time']

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
    list_display = ['title', 'host', 'get_slots_display', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProgramScheduleInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'host', 'category', 'image', 'is_active', 'order')
        }),
        ('Legacy (optional, ignored if this program has Time Slots below)', {
            'classes': ('collapse',),
            'fields': ('start_time', 'end_time', 'days', 'is_live'),
        }),
    )

    def get_slots_display(self, obj):
        slots = obj.schedules.all()
        if not slots:
            return "— no time slots —"
        return "; ".join(
            f"{s.get_days_display()} {s.start_time.strftime('%H:%M')}-{s.end_time.strftime('%H:%M')}"
            for s in slots
        )
    get_slots_display.short_description = "Time Slots"

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


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ['path', 'ip_address', 'session_key', 'created_at']
    list_filter = ['created_at']
    search_fields = ['path', 'ip_address', 'session_key']
    date_hierarchy = 'created_at'
    readonly_fields = ['path', 'session_key', 'ip_address', 'user_agent', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
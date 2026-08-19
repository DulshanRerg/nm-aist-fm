from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator

class Frequency(models.Model):
    """Radio frequency for Nelson Mandela Radio"""
    LOCATION_CHOICES = [
        ('dar_es_salaam', 'Dar es Salaam'),
        ('zanzibar', 'Zanzibar'),
        ('pwani', 'Pwani'),
        ('tanga', 'Tanga'),
        ('arusha', 'Arusha'),
        ('mwanza', 'Mwanza'),
        ('dodoma', 'Dodoma'),
        ('mbeya', 'Mbeya'),
        ('other', 'Other'),
    ]
    
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, default='arusha')
    custom_location = models.CharField(max_length=100, blank=True, help_text="Use if 'other' is selected above")
    frequency = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        validators=[MinValueValidator(87.5), MaxValueValidator(108.0)]
    )
    slogan = models.CharField(max_length=200, default="Mandela's voice across Tanzania")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Frequencies"
        ordering = ['order', 'location']
    
    def __str__(self):
        location_name = dict(self.LOCATION_CHOICES).get(self.location, self.location)
        if self.custom_location and self.location == 'other':
            location_name = self.custom_location
        return f"{self.frequency} MHz - {location_name}"
    
    def get_full_location(self):
        """Get the full location name"""
        if self.location == 'other' and self.custom_location:
            return self.custom_location
        return dict(self.LOCATION_CHOICES).get(self.location, self.location)

class News(models.Model):
    """News articles for the radio station"""
    CATEGORY_CHOICES = [
        ('local', 'Local News'),
        ('national', 'National News'),
        ('international', 'International News'),
        ('sports', 'Sports'),
        ('entertainment', 'Entertainment'),
        ('politics', 'Politics'),
        ('business', 'Business'),
        ('health', 'Health'),
        ('education', 'Education'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=300, blank=True)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='local')
    author = models.CharField(max_length=100, default="Nelson Mandela Radio")
    image = models.ImageField(upload_to='news/images/', blank=True, null=True)
    image_caption = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    publish_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "News"
        ordering = ['-publish_date', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f"/news/{self.slug}/"
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

class Program(models.Model):
    """Radio programs/schedules"""
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
        ('daily', 'Daily'),
        ('weekdays', 'Weekdays'),
        ('weekends', 'Weekends'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    host = models.ForeignKey('Member', on_delete=models.SET_NULL, null=True, blank=True)
    # Legacy single-slot fields. Kept (optional) for backward compatibility only —
    # scheduling now happens through the related ProgramSchedule "time slots" below,
    # so one Program can air at several different times without duplicating the
    # whole program entry.
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    days = models.CharField(max_length=20, choices=DAY_CHOICES, default='daily', blank=True)
    is_live = models.BooleanField(default=False)
    category = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='programs/images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_duration(self):
        """Calculate legacy single-slot program duration in hours (kept for backward compat)."""
        from datetime import datetime, timedelta
        if not self.start_time or not self.end_time:
            return ""
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        if end < start:
            end += timedelta(days=1)
        duration = end - start
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    
    def get_days_display(self):
        """Return the display value for the legacy days field."""
        return dict(self.DAY_CHOICES).get(self.days, self.days)

    # Concrete weekdays a given `days` choice value expands to.
    WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    WEEKENDS = ['saturday', 'sunday']
    ALL_DAYS = WEEKDAYS + WEEKENDS

    @classmethod
    def expand_days(cls, days_value):
        """Turn 'daily' / 'weekdays' / 'weekends' / a single day into a list of
        concrete weekday keys ('monday', 'tuesday', ...)."""
        if days_value == 'daily':
            return list(cls.ALL_DAYS)
        if days_value == 'weekdays':
            return list(cls.WEEKDAYS)
        if days_value == 'weekends':
            return list(cls.WEEKENDS)
        if days_value in cls.ALL_DAYS:
            return [days_value]
        return []


class ProgramSchedule(models.Model):
    """A single air-time slot for a Program.

    This is what lets one program (e.g. "Habari") be entered once — title,
    host, description, image — and then broadcast at several different times
    (e.g. 06:00-06:20 and again at 07:00-07:30) by simply adding more slots,
    instead of duplicating the whole Program.
    """
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='schedules')
    days = models.CharField(max_length=20, choices=Program.DAY_CHOICES, default='daily',
                             help_text="Choose 'Weekdays' for Mon-Fri, 'Weekends' for Sat-Sun, "
                                       "'Daily' for every day, or a single day.")
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_live = models.BooleanField(default=False, help_text="Broadcast live during this slot")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'start_time']
        verbose_name = "Time Slot"
        verbose_name_plural = "Time Slots"

    def __str__(self):
        return f"{self.program.title} — {self.get_days_display()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"

    def get_days_display(self):
        return dict(Program.DAY_CHOICES).get(self.days, self.days)

    def get_duration(self):
        """Calculate slot duration, e.g. '1h 30m'."""
        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        if end < start:
            end += timedelta(days=1)
        duration = end - start
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        if hours and minutes:
            return f"{hours}h {minutes}m"
        if hours:
            return f"{hours}h"
        return f"{minutes}m"

    def expanded_days(self):
        """Concrete weekday keys this slot airs on."""
        return Program.expand_days(self.days)

class LiveStream(models.Model):
    """Live stream configuration"""
    STREAM_TYPE_CHOICES = [
        ('icecast', 'Icecast'),
        ('shoutcast', 'Shoutcast'),
        ('hls', 'HLS'),
        ('mp3', 'MP3 Direct'),
    ]
    
    name = models.CharField(max_length=100, default="Nelson Mandela Radio")
    stream_url = models.URLField()
    backup_stream_url = models.URLField(blank=True)
    stream_type = models.CharField(max_length=20, choices=STREAM_TYPE_CHOICES, default='icecast')
    is_active = models.BooleanField(default=True)
    metadata_url = models.URLField(blank=True, help_text="URL for current song/artist metadata")
    bitrate = models.PositiveIntegerField(default=128, help_text="Bitrate in kbps")
    current_listeners = models.PositiveIntegerField(default=0, editable=False)
    max_listeners = models.PositiveIntegerField(default=1000)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Live Stream"
        verbose_name_plural = "Live Streams"
    
    def __str__(self):
        return f"{self.name} - {self.bitrate}kbps"

class ContactMessage(models.Model):
    """Contact form messages"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    is_subscribed = models.BooleanField(default=True, help_text="Subscribe to newsletter")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject or 'No Subject'}"

class SocialMedia(models.Model):
    """Social media links"""
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter/X'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('linkedin', 'LinkedIn'),
        ('spotify', 'Spotify'),
        ('apple_music', 'Apple Music'),
    ]
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField()
    display_name = models.CharField(max_length=100, blank=True)
    icon_class = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Social Media"
        ordering = ['order', 'platform']
    
    def __str__(self):
        return f"{self.get_platform_display()}: {self.display_name or self.url}"
    
    def get_icon_class(self):
        """Get Font Awesome icon class for the platform"""
        icons = {
            'facebook': 'fab fa-facebook-f',
            'twitter': 'fab fa-twitter',
            'instagram': 'fab fa-instagram',
            'youtube': 'fab fa-youtube',
            'tiktok': 'fab fa-tiktok',
            'whatsapp': 'fab fa-whatsapp',
            'telegram': 'fab fa-telegram',
            'linkedin': 'fab fa-linkedin-in',
            'spotify': 'fab fa-spotify',
            'apple_music': 'fab fa-apple',
        }
        return self.icon_class or icons.get(self.platform, 'fas fa-link')
    
    def get_platform_display(self):
        """Return the display value for platform."""
        return dict(self.PLATFORM_CHOICES).get(self.platform, self.platform)

class SiteSetting(models.Model):
    """General site settings"""
    site_name = models.CharField(max_length=100, default="Nelson Mandela Radio")
    slogan = models.CharField(max_length=200, default="Radio ya Mandela - Hapa ni Nyumbani")
    logo = models.ImageField(upload_to='site/logo/', blank=True)
    favicon = models.ImageField(upload_to='site/favicon/', blank=True)
    primary_color = models.CharField(max_length=7, default="#f3c242", help_text="Hex color code")
    secondary_color = models.CharField(max_length=7, default="#f2b827", help_text="Hex color code")
    contact_email = models.EmailField(default="info@mandelaradio.co.tz")
    contact_phone = models.CharField(max_length=20, default="+255 123 456 789")
    address = models.TextField(blank=True)
    about_text = models.TextField(blank=True)
    facebook_pixel = models.TextField(blank=True, help_text="Facebook Pixel code")
    google_analytics = models.TextField(blank=True, help_text="Google Analytics code")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        """Load or create the singleton instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class AdBanner(models.Model):
    """Advertisement banners"""
    POSITION_CHOICES = [
        ('header', 'Header'),
        ('sidebar', 'Sidebar'),
        ('footer', 'Footer'),
        ('home_top', 'Home Page Top'),
        ('home_middle', 'Home Page Middle'),
        ('home_bottom', 'Home Page Bottom'),
    ]
    
    title = models.CharField(max_length=200)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    image = models.ImageField(upload_to='ads/banners/')
    url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0, editable=False)
    clicks_count = models.PositiveIntegerField(default=0, editable=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"
    
    def is_current(self):
        """Check if the ad is currently active based on dates"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.start_date and self.start_date > today:
            return False
        if self.end_date and self.end_date < today:
            return False
        return True
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_clicks(self):
        self.clicks_count += 1
        self.save(update_fields=['clicks_count'])
    
    def get_position_display(self):
        """Return the display value for position."""
        return dict(self.POSITION_CHOICES).get(self.position, self.position)
    
class PodcastEpisode(models.Model):
    """Podcast episodes"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    audio_file = models.FileField(upload_to='podcasts/episodes/')
    duration = models.DurationField(blank=True, null=True)
    publish_date = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-publish_date', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f"/podcasts/{self.slug}/"
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def get_duration_display(self):
        """Return duration in HH:MM:SS format"""
        if self.duration:
            total_seconds = int(self.duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return "00:00:00"
    
    def get_publish_date_display(self):
        """Return formatted publish date"""
        return self.publish_date.strftime("%B %d, %Y")


class MembershipApplication(models.Model):
    """Membership applications for the radio station"""
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    motivation = models.TextField(help_text="Why do you want to join Nelson Mandela Radio?")
    resume = models.FileField(upload_to='memberships/resumes/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {'Approved' if self.is_approved else 'Pending'}"
    
    def approve(self):
        self.is_approved = True
        self.reviewed_at = timezone.now()
        self.save(update_fields=['is_approved', 'reviewed_at'])

    def get_application_duration(self):
        """Get duration since application was created"""
        delta = timezone.now() - self.created_at
        return delta.days + 1  # Including the current day
    
    def get_status_display(self):
        """Return application status"""
        return "Approved" if self.is_approved else "Pending"
    

class Member(models.Model):
    """Members of the radio station"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='members/profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_membership_duration(self):
        """Get duration of membership in days"""
        delta = timezone.now() - self.created_at
        return delta.days
    
    def get_status_display(self):
        """Return member status"""
        return "Active" if self.is_active else "Inactive"


class PageVisit(models.Model):
    """One row per page view, used to power the admin visitor dashboard.

    A "visitor" is counted as a unique session_key; a "page view" is every
    row. Excludes admin, static, media and API/AJAX requests (see
    VisitorTrackingMiddleware).
    """
    path = models.CharField(max_length=500)
    session_key = models.CharField(max_length=40, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Page Visit"
        verbose_name_plural = "Page Visits"

    def __str__(self):
        return f"{self.path} — {self.created_at:%Y-%m-%d %H:%M}"

    

    

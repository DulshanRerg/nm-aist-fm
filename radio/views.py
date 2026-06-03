from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
import json
import requests
from django.http import StreamingHttpResponse
from .models import Frequency, News, Program, LiveStream, ContactMessage, SiteSetting, Member

def home(request):
    """Home page view"""
    frequencies = Frequency.objects.filter(is_active=True).order_by('order')
    featured_news = News.objects.filter(is_featured=True, is_published=True)[:3]
    current_programs = Program.objects.filter(is_active=True, is_live=True)[:3]
    site_settings = SiteSetting.load()

    context = {
        'frequencies': frequencies,
        'featured_news': featured_news,
        'current_programs': current_programs,
        'site_settings': site_settings,
        'page_title': f'{site_settings.site_name} - {site_settings.slogan}'
    }
    return render(request, 'home.html', context)

def about(request):
    """About page view"""
    site_settings = SiteSetting.load()
    members = Member.objects.filter(is_active=True)
    context = {
        'site_settings': site_settings,
        'page_title': f'About Us - {site_settings.site_name}',
        'members': members
    }
    return render(request, 'about.html', context)

def live_stream(request):
    """Live streaming page"""
    stream = LiveStream.objects.filter(is_active=True).first()
    current_program = Program.objects.filter(is_active=True, is_live=True).first()
    site_settings = SiteSetting.load()

    # Get ALL active programs
    all_programs = Program.objects.filter(is_active=True).order_by('order', 'start_time')

    # Group programs by day
    programs_by_day = {}
    for program in all_programs:
        if program.days == 'daily':
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                if day not in programs_by_day:
                    programs_by_day[day] = []
                programs_by_day[day].append(program)
        elif program.days == 'weekdays':
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                if day not in programs_by_day:
                    programs_by_day[day] = []
                programs_by_day[day].append(program)
        elif program.days == 'weekends':
            for day in ['saturday', 'sunday']:
                if day not in programs_by_day:
                    programs_by_day[day] = []
                programs_by_day[day].append(program)
        else:
            if program.days not in programs_by_day:
                programs_by_day[program.days] = []
            programs_by_day[program.days].append(program)

    context = {
        'stream': stream,
        'current_program': current_program,
        'all_programs': all_programs,
        'programs_by_day': programs_by_day,
        'day_choices': dict(Program.DAY_CHOICES),
        'site_settings': site_settings,
        'page_title': f'Listen Live - {site_settings.site_name}'
    }
    return render(request, 'live_stream.html', context)

def news_list(request):
    """News listing page"""
    news_list = News.objects.filter(is_published=True, publish_date__lte=timezone.now())

    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        news_list = news_list.filter(category=category)

    # Pagination
    paginator = Paginator(news_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    site_settings = SiteSetting.load()

    context = {
        'page_obj': page_obj,
        'category': category,
        'categories': dict(News.CATEGORY_CHOICES),
        'site_settings': site_settings,
        'page_title': f'News - {site_settings.site_name}'
    }
    return render(request, 'news_list.html', context)

def news_detail(request, slug):
    """News detail page"""
    news = get_object_or_404(News, slug=slug, is_published=True)

    # Increment view count
    news.increment_views()

    # Get related news
    related_news = News.objects.filter(
        category=news.category,
        is_published=True
    ).exclude(id=news.id)[:3]

    site_settings = SiteSetting.load()

    context = {
        'news': news,
        'related_news': related_news,
        'site_settings': site_settings,
        'page_title': f'{news.title} - {site_settings.site_name}'
    }
    return render(request, 'news_detail.html', context)

def programs(request):
    """Programs listing page"""
    programs_list = Program.objects.filter(is_active=True).order_by('order', 'start_time')

    # Group by day
    programs_by_day = {}
    for program in programs_list:
        if program.days == 'daily':
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                if day not in programs_by_day:
                    programs_by_day[day] = []
                programs_by_day[day].append(program)
        elif program.days == 'weekdays':
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                if day not in programs_by_day:
                    programs_by_day[day] = []
                programs_by_day[day].append(program)
        elif program.days == 'weekends':
            for day in ['saturday', 'sunday']:
                if day not in programs_by_day:
                    programs_by_day[day] = []
                programs_by_day[day].append(program)
        else:
            if program.days not in programs_by_day:
                programs_by_day[program.days] = []
            programs_by_day[program.days].append(program)

    site_settings = SiteSetting.load()

    context = {
        'programs_by_day': programs_by_day,
        'day_choices': dict(Program.DAY_CHOICES),
        'site_settings': site_settings,
        'page_title': f'Programs - {site_settings.site_name}'
    }
    return render(request, 'programs.html', context)

@require_POST
@csrf_exempt
def contact(request):
    """Handle contact form submission (now with subject field and user email as sender)"""
    try:
        data = json.loads(request.body) if request.body else request.POST
    except:
        data = request.POST

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    subject = data.get('subject', '').strip() or 'Contact Form Message'
    message = data.get('message', '').strip()

    # Validation
    if not email or not subject or not message:
        return JsonResponse({
            'success': False,
            'error': 'Please fill in all required fields.'
        })

    # Save to database
    contact_message = ContactMessage.objects.create(
        name=name or email,  # fallback to email if name not provided
        email=email,
        subject=subject,
        message=message,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    # Send email to admin
    try:
        send_mail(
            subject=f"Contact Form: {subject}",
            message=f"From: {email}\nSubject: {subject}\nMessage:\n{message}",
            from_email=email,  # user email as sender
            recipient_list=["nelsonmandela.fm@nm-aist.ac.tz"],
            fail_silently=False,
        )
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Failed to send email. Please try again later.'})

    return JsonResponse({
        'success': True,
        'message': 'Thank you for your message. We will get back to you soon.'
    })

def contact_page(request):
    """Contact page view"""
    site_settings = SiteSetting.load()

    context = {
        'site_settings': site_settings,
        'page_title': f'Contact Us - {site_settings.site_name}'
    }
    return render(request, 'contact.html', context)

def frequencies_json(request):
    """API endpoint for frequencies in JSON format"""
    frequencies = list(Frequency.objects.filter(is_active=True).values(
        'frequency',
        'location',
        'slogan',
        'description'
    ))

    # Convert Decimal to string for JSON serialization
    for freq in frequencies:
        freq['frequency'] = str(freq['frequency'])
        freq['location_name'] = dict(Frequency.LOCATION_CHOICES).get(freq['location'], freq['location'])

    return JsonResponse(frequencies, safe=False)

def get_current_program(request):
    """API endpoint for current program"""
    now = timezone.now()
    current_time = now.time()
    current_day = now.strftime('%A').lower()

    # Find current program
    current_program = Program.objects.filter(
        is_active=True,
        is_live=True
    ).first()

    if current_program:
        program_data = {
            'title': current_program.title,
            'host': current_program.host,
            'description': current_program.description,
            'start_time': current_program.start_time.strftime('%H:%M'),
            'end_time': current_program.end_time.strftime('%H:%M'),
            'image_url': current_program.image.url if current_program.image else None
        }
    else:
        program_data = {
            'title': 'General Programming',
            'host': 'Various DJs',
            'description': 'Enjoy a mix of music and entertainment',
            'start_time': '00:00',
            'end_time': '23:59',
            'image_url': None
        }

    return JsonResponse(program_data)


@require_GET
def now_playing_api(request):
    """API endpoint for current song information"""
    try:
        # Try to fetch from your stream metadata
        # This is a placeholder - you'll need to integrate with your stream server

        # For Icecast/Shoutcast streams, you might fetch metadata from:
        # stream_url + '/status-json.xsl' or similar

        data = {
            "title": "Muziki Bora wa Kizazi Kipya",
            "artist": "DJ Mandela",
            "album": "Nelson Mandela FM",
            "listeners": 1250,
            "bitrate": 128,
            "format": "audio/mp3"
        }
    except:
        # Fallback data
        data = {
            "title": "Live Broadcast",
            "artist": "Nelson Mandela Radio",
            "album": "",
            "listeners": 0,
            "bitrate": 128,
            "format": "audio/mp3"
        }

    return JsonResponse(data)


def get_members(request):
    """API endpoint for fetching members"""
    members = Member.objects.filter(is_active=True).values(
        'first_name',
        'bio',
        'profile_picture'
    )

    member_list = []
    for member in members:
        member_data = {
            'first_name': member['first_name'],
            'bio': member['bio'],
            'photo_url': member['profile_picture'].url if member['profile_picture'] else None
        }
        member_list.append(member_data)

    data = {
        'members': member_list
    }

    return JsonResponse(data)

@require_GET
@csrf_exempt
def stream_proxy(request):
    """Proxy audio stream for development to bypass CORS."""
    stream_url = 'http://41.93.85.231:5000/'  # or the full stream endpoint
    try:
        r = requests.get(stream_url, stream=True, timeout=10)
        response = StreamingHttpResponse(r.iter_content(chunk_size=8192), content_type=r.headers.get('Content-Type', 'audio/mpeg'))
        response['Access-Control-Allow-Origin'] = '*'
        response['Cache-Control'] = 'no-cache'
        return response
    except Exception as e:
        return HttpResponse('Stream unavailable', status=502)
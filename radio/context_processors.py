from django.utils import timezone


def visitor_summary(request):
    """Adds a cheap, cached-per-request visitor summary to every template's
    context. Only meaningfully used in the Django admin homepage override,
    but harmless (one indexed aggregate query) everywhere else.
    """
    if not (request.path.startswith('/admin/') and getattr(request, 'user', None) and request.user.is_staff):
        return {}

    from .models import PageVisit
    now = timezone.localtime(timezone.now())
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    all_visits = PageVisit.objects.all()
    return {
        'admin_total_visitors': all_visits.values('session_key').distinct().count(),
        'admin_today_visitors': all_visits.filter(created_at__gte=today_start).values('session_key').distinct().count(),
        'admin_total_pageviews': all_visits.count(),
    }

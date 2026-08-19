from .models import PageVisit

# Prefixes we never want to count as a "visit" — admin traffic, static/media
# files, and JSON/API endpoints polled by the player (those aren't a person
# looking at a new page, they're the audio player checking for updates).
EXCLUDED_PREFIXES = (
    '/admin/',
    '/static/',
    '/media/',
    '/api/',
    '/dashboard/',
    '/dev-stream/',
    '/favicon.ico',
)


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class VisitorTrackingMiddleware:
    """Logs one PageVisit per real page view.

    Must run after SessionMiddleware (so request.session exists) — it's
    placed after it in settings.MIDDLEWARE.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            if (
                request.method == 'GET'
                and response.status_code < 400
                and not request.path.startswith(EXCLUDED_PREFIXES)
                and not getattr(request, 'is_ajax_poll', False)
            ):
                if not request.session.session_key:
                    request.session.save()
                PageVisit.objects.create(
                    path=request.path[:500],
                    session_key=request.session.session_key or '',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:300],
                )
        except Exception:
            # Visitor tracking must never break the site.
            pass

        return response

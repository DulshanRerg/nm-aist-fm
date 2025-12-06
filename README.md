# Nelson Mandela Radio - Django Project (Starter)

This is a starter Django full-stack project that clones the common structure of a radio station website.
It includes:
- Live streaming player (configure streaming URL via admin)
- News posts (with image upload)
- Programs schedule
- About and Contact pages
- Admin configured for content management

## Quick start (local development)

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # on macOS / Linux
   .venv\Scripts\activate    # on Windows (PowerShell)
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations and create superuser:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. Collect static (optional) and run server:
   ```bash
   python manage.py collectstatic --noinput
   python manage.py runserver
   ```

5. Open http://127.0.0.1:8000/ and login to admin at /admin/ to add News, Programs, and SiteConfig.

## Notes
- Update `nmandela/settings.py` SECRET_KEY and DEBUG for production.
- Configure allowed hosts, static/media storage, and HTTPS before deploying.
- This is intended as a starting template you can customize and extend.

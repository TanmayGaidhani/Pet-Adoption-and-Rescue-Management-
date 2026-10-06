"""
WSGI config for myproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import threading
import time
import urllib.request

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = get_wsgi_application()


def _keep_alive_worker():
    """Background worker to keep Render free tier alive by pinging /health/ every 10 minutes"""
    base_url = os.getenv('RENDER_EXTERNAL_URL', 'https://pet-adoption-and-rescue-management.onrender.com').rstrip('/')
    url = f"{base_url}/health/"
    # Initial delay of 2 minutes before starting pings
    time.sleep(120)
    while True:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'RescueMate-KeepAlive/1.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                print(f"[KeepAlive] Pinged {url} -> status {resp.status}")
        except Exception as e:
            print(f"[KeepAlive] Ping warning: {e}")
        time.sleep(600)  # Ping every 10 minutes (600s < Render's 900s sleep threshold)


# Start background keep-alive thread in production (Render)
if os.getenv('RENDER') or os.getenv('RENDER_EXTERNAL_URL') or (os.getenv('DEBUG', 'True') == 'False'):
    t = threading.Thread(target=_keep_alive_worker, daemon=True)
    t.start()


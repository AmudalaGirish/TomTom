import os
from django.core.asgi import get_asgi_application
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
# import maps.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    # 'websocket': URLRouter(
    #     maps.routing.websocket_urlpatterns
    # ),
})

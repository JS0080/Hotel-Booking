from django.conf.urls import url
from django.contrib import admin
from .views import *


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', hotels),
    url(r'^search_hotel/$', search_hotel),
]

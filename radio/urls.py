from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('live_stream/', views.live_stream, name='live_stream'),
    path('stream/', views.stream_proxy, name='stream'),
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('programs/', views.programs, name='programs'),
    path('contact/', views.contact_page, name='contact'),
    path('api/contact/', views.contact, name='contact_api'),
    path('api/frequencies/', views.frequencies_json, name='frequencies_json'),
    path('api/current-program/', views.get_current_program, name='current_program'),
    path('api/now-playing/', views.now_playing_api, name='now_playing_api'),
    path('api/members/', views.get_members, name='get_members'),
    path('dev-stream/', views.stream_proxy, name='dev_stream'),
]
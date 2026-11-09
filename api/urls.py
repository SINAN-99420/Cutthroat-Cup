from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'leagues', LeagueViewSet, basename='leagues')
router.register(r'matches', MatchViewSet, basename='matches')

urlpatterns = [
    path('dashboard/', get_dashboard_data, name='dashboard'),
    path('account/', account_view, name='account'),
    path('settings/', settings_view, name='settings'),
    path('activity/', activity_view, name='activity'),
    path('draft/', draft_view, name='draft'),
    path('waivers/', waivers_view, name='waivers'),
    path('conflicts/', conflict_view, name='conflicts'),
    path('', include(router.urls)),
]
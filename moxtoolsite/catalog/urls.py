from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('tracks/', views.TrackListView.as_view(), name='tracks'),
    path("track/<int:pk>/", views.TrackDetailView.as_view(), name='track-detail'),
]
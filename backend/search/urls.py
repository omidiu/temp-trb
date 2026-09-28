from django.urls import path

from . import views

urlpatterns = [
    path("intent/parse", views.IntentParseView.as_view()),
    path("needs", views.NeedsView.as_view()),
    path("search", views.SearchView.as_view()),
]

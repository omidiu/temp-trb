from django.urls import path

from . import views

urlpatterns = [
    path("intent/parse", views.IntentParseView.as_view()),
    path("needs", views.NeedsView.as_view()),
    path("search", views.SearchView.as_view()),
    path("offers/<int:pk>", views.OfferDetailView.as_view()),
    path("explain", views.ExplainView.as_view()),
]

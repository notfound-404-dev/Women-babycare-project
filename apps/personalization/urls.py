from django.urls import path

from .views import RecommendationListView

app_name = "personalization"

urlpatterns = [
    path("", RecommendationListView.as_view(), name="list"),
]

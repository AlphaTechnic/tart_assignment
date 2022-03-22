from django.urls import path
from .views import ListView, InfoView

app_name = "fundings_app"

urlpatterns = [
    path('v1/startups/', ListView.as_view(), name="startup_list"),
    path('v1/startups/<str:platform>/<int:identifier>', InfoView.as_view(), name="startup_info"),
]
from django.urls import path
from .views import analyze_fraud

urlpatterns = [
    path("analyze/", analyze_fraud, name="analyze_fraud"),
]
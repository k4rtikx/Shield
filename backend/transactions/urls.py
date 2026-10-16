from django.urls import path
from .views import transfer, transaction_history

urlpatterns = [
    path('transfer/', transfer, name='transfer'),
    path('history/', transaction_history, name='transaction_history'),
]
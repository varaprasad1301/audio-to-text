from django.urls import path
from .views import AudioToExpenseView

urlpatterns = [
    path('upload-audio/', AudioToExpenseView.as_view(), name='upload-audio'),
]

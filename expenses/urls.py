from django.urls import path
from .views import AudioToExpenseView
from .views import scan_receipt

urlpatterns = [
    path('upload-audio/', AudioToExpenseView.as_view(), name='upload-audio'),
    path('scan-receipt/', scan_receipt, name='scan_receipt'),
]

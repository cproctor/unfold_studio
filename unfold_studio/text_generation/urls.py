from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('generate', csrf_exempt(views.GenerateTextView.as_view()), name="generate")
]


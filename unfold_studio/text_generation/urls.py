from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('generate', csrf_exempt(views.GenerateTextView.as_view()), name="generate")
]


from django.urls import path
from . import views

urlpatterns = [
    path('generate', views.GenerateTextView.as_view(), name="generate")
]


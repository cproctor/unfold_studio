from django.urls import path
from . import views

urlpatterns = [
    path("compile", views.compile_story, name="compile"),
]

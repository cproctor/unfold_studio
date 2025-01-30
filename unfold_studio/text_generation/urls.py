from django.urls import path
from . import views

urlpatterns = [
    path('generate', views.GenerateTextView.as_view(), name="generate"),
    path('get_next_action', views.GetNextActionView.as_view(), name="get_next_action")
]


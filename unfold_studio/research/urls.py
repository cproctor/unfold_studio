from django.urls import path
from . import views

urlpatterns = [
    path("compile", views.compile_story, name="compile"),
    path("api-key/", views.ResearcherAPIKeyView.as_view(), name="researcher_api_key"),
]

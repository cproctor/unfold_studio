"""unfold_studio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from unfold_studio import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name="home"),
    url(r'about', views.about, name="about"),
    url(r'documentation', views.documentation, name="documentation"),
    url(r'stories/new/?', views.new_story, name="new_story"),
    url(r'stories/(?P<story_id>\d+)/?$', views.show_story, name="show_story"), 
    url(r'stories/(?P<story_id>\d+)/json/?$', views.show_json, name="show_json"), 
    url(r'stories/(?P<story_id>\d+)/ink/?$', views.show_ink, name="show_ink"), 
    url(r'stories/(?P<story_id>\d+)/edit/?$', views.edit_story, name="edit_story"), 
    #url(r'stories/(?P<story_id>\d+)/delete/?$', views.delete_story, name="delete_story"), 
]

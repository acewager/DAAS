from django.urls import path

from apps.instances.views_volumes import VolumeListView

urlpatterns = [path("", VolumeListView.as_view(), name="volume-list")]

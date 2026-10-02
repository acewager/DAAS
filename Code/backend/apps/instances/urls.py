from django.urls import path
from .views import InstanceLaunchView, InstanceListView

urlpatterns = [
    path("", InstanceListView.as_view(), name="instance-list"),
    path("<uuid:instance_id>/launch/", InstanceLaunchView.as_view(), name="instance-launch"),
]

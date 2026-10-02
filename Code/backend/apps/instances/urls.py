from django.urls import path
from .views import InstanceDeleteView, InstanceLaunchView, InstanceListView, InstanceRestartView, InstanceStartView, InstanceStopView

urlpatterns = [
    path("", InstanceListView.as_view(), name="instance-list"),
    path("<uuid:instance_id>/launch/", InstanceLaunchView.as_view(), name="instance-launch"),
    path("<uuid:instance_id>/start/", InstanceStartView.as_view(), name="instance-start"),
    path("<uuid:instance_id>/stop/", InstanceStopView.as_view(), name="instance-stop"),
    path("<uuid:instance_id>/restart/", InstanceRestartView.as_view(), name="instance-restart"),
    path("<uuid:instance_id>/", InstanceDeleteView.as_view(), name="instance-delete"),
]

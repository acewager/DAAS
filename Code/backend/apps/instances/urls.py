from django.urls import path
from .views import InstanceListView

urlpatterns = [path("", InstanceListView.as_view(), name="instance-list")]

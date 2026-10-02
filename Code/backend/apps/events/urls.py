from django.urls import path

from .views import EventHistoryView

urlpatterns = [path("", EventHistoryView.as_view(), name="event-list")]

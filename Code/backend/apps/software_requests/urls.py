from django.urls import path

from .views import SoftwareRequestApproveView, SoftwareRequestDetailView, SoftwareRequestListCreateView, SoftwareRequestRejectView

urlpatterns = [
    path("", SoftwareRequestListCreateView.as_view(), name="software-request-list"),
    path("<uuid:request_id>/", SoftwareRequestDetailView.as_view(), name="software-request-detail"),
    path("<uuid:request_id>/approve/", SoftwareRequestApproveView.as_view(), name="software-request-approve"),
    path("<uuid:request_id>/reject/", SoftwareRequestRejectView.as_view(), name="software-request-reject"),
]

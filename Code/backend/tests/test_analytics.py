from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.analytics.models import Analytics
from apps.instances.models import DesktopInstance, InstanceStatus
from apps.templates.models import DesktopTemplate


def auth_client(user):
    client = APIClient(); client.force_authenticate(user)
    return client


def make_running_instance(user, name="Mine"):
    template, _ = DesktopTemplate.objects.get_or_create(
        name="Minimal", slug="minimal", defaults={"json_configuration": {"image": "desktop:minimal"}}
    )
    return DesktopInstance.objects.create(user=user, template=template, name=name, cpu_limit="2", memory_limit="2G", status=InstanceStatus.RUNNING)


@pytest.mark.django_db
def test_sample_instance_creates_analytics_from_container_usage():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    instance = make_running_instance(user)

    with patch("docker_manager.manager.docker_manager.container_usage", return_value={"cpu_percent": 10.0, "ram_mb": 500.0}):
        from services.analytics_service import AnalyticsService
        analytics = AnalyticsService.sample_instance(instance)

    assert analytics is not None
    assert analytics.cpu_average == 10.0
    assert analytics.ram_average == 500.0
    assert analytics.uptime_seconds >= 0
    assert analytics.last_calculated is not None

    # A second sample folds into the smoothing average.
    with patch("docker_manager.manager.docker_manager.container_usage", return_value={"cpu_percent": 20.0, "ram_mb": 700.0}):
        analytics = AnalyticsService.sample_instance(instance)
    assert analytics.cpu_average == 15.0
    assert analytics.ram_average == 600.0


@pytest.mark.django_db
def test_sample_skips_missing_containers():
    user = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    instance = make_running_instance(user)
    with patch("docker_manager.manager.docker_manager.container_usage", return_value=None):
        from services.analytics_service import AnalyticsService
        assert AnalyticsService.sample_instance(instance) is None
    assert not Analytics.objects.exists()


@pytest.mark.django_db
def test_aggregation_task_samples_running_instances_only():
    owner = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    running = make_running_instance(owner)
    stopped = make_running_instance(owner, name="Stopped")
    stopped.status = InstanceStatus.STOPPED
    stopped.save(update_fields=["status"])

    with patch("docker_manager.manager.docker_manager.container_usage", return_value={"cpu_percent": 5.0, "ram_mb": 300.0}) as usage_mock:
        from tasks.analytics import aggregate_usage
        result = aggregate_usage()
        assert usage_mock.call_count == 1  # only the RUNNING instance sampled
    assert result == {"sampled": 1}
    assert Analytics.objects.filter(instance=running).exists()
    assert not Analytics.objects.filter(instance=stopped).exists()


@pytest.mark.django_db
def test_usage_endpoint_is_scoped_and_returns_zeros_without_analytics():
    owner = User.objects.create_user("owner", "owner@example.com", "SecurePass123!")
    other = User.objects.create_user("other", "other@example.com", "SecurePass123!")
    admin = User.objects.create_user("admin", "admin@example.com", "SecurePass123!", role=UserRole.ADMIN)
    mine = make_running_instance(owner)
    theirs = make_running_instance(owner, name="Mine too")

    # The owner sees their own; another user is denied.
    response = auth_client(owner).get(reverse("analytics-instance-usage", kwargs={"instance_id": str(mine.id)}))
    assert response.status_code == 200
    assert response.data["data"]["cpu_average"] == 0.0  # no analytics yet

    assert auth_client(other).get(reverse("analytics-instance-usage", kwargs={"instance_id": str(mine.id)})).status_code == 404

    # Admins can view any instance's usage.
    response = auth_client(admin).get(reverse("analytics-instance-usage", kwargs={"instance_id": str(theirs.id)}))
    assert response.status_code == 200

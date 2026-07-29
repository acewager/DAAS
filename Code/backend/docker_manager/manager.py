"""
DockerManager — the ONLY component permitted to communicate with Docker.

Per 05_Container_Architecture.md Section 16 and 06_Backend_Architecture.md
Section 7:

- No API view, serializer, or React component may import the Docker SDK.
- All container lifecycle operations flow through this class.
- Long-running operations are invoked from Celery tasks, never
  synchronously from a request/response cycle.

This is a foundation-slice skeleton: methods are stubbed out and will be
implemented alongside Instance Provisioning (Sprint 3 / M4).
"""
import logging

import docker
from django.conf import settings

logger = logging.getLogger("docker_manager")


class DockerManagerError(Exception):
    """Raised when a Docker operation fails in a way callers must handle."""


class DockerManager:
    """Thin, testable wrapper around the Docker SDK (docker-py)."""

    def __init__(self):
        self._client = None

    @property
    def client(self) -> "docker.DockerClient":
        """Lazily create the Docker SDK client using DOCKER_HOST from settings."""
        if self._client is None:
            self._client = docker.DockerClient(base_url=settings.DOCKER_HOST)
        return self._client

    def ping(self) -> bool:
        """Used by health checks to confirm the Docker daemon is reachable."""
        try:
            return self.client.ping()
        except Exception as exc:  # noqa: BLE001 — surfaced to health check
            logger.warning("Docker daemon unreachable: %s", exc)
            return False

    # -- Container lifecycle (implemented in M4 — Instance Provisioning) ----

    def create_container(self, *, instance, template):
        raise NotImplementedError("Implemented alongside VS-024 (Sprint 3).")

    def start_container(self, *, instance):
        raise NotImplementedError("Implemented alongside VS-035 (Sprint 5).")

    def stop_container(self, *, instance):
        raise NotImplementedError("Implemented alongside VS-036 (Sprint 5).")

    def restart_container(self, *, instance):
        raise NotImplementedError("Implemented alongside VS-037 (Sprint 5).")

    def delete_container(self, *, instance):
        raise NotImplementedError("Implemented alongside VS-038 (Sprint 5).")


# Module-level singleton — services import this rather than instantiating
# DockerManager directly, so it stays mockable in tests
# (06_Backend_Architecture.md Section 17).
docker_manager = DockerManager()

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
        try:
            config = template.json_configuration
            volumes = {f"dcp-data-{instance.id}": {"bind": "/home/user", "mode": "rw"}} if instance.persistent else None
            # VS-026: each instance gets a hash-based subdomain routed by
            # Traefik to the container's web UI (ADR-011). M6: every request
            # passes the desktop-auth ForwardAuth middleware first, which
            # validates the session and instance ownership before routing
            # (05_Container_Architecture.md Section 13).
            web_port = config.get("web_port", 3000)
            router = f"desktop-{instance.id}"
            labels = {
                "traefik.enable": "true",
                f"traefik.http.routers.{router}.rule": f"Host(`{instance.subdomain}`)",
                f"traefik.http.routers.{router}.service": router,
                f"traefik.http.routers.{router}.middlewares": "desktop-auth@docker",
                f"traefik.http.services.{router}.loadbalancer.server.port": str(web_port),
            }
            container = self.client.containers.create(config["image"], name=instance.container_name, hostname=f"inst-{str(instance.id)[:8]}", detach=True, mem_limit=instance.memory_limit, nano_cpus=int(float(instance.cpu_limit) * 1_000_000_000), volumes=volumes, network="dcp-network", labels=labels)
            container.start()
            return container
        except Exception as exc:
            raise DockerManagerError(str(exc)) from exc

    def start_container(self, *, instance):
        try:
            container = self.client.containers.get(instance.container_name)
            container.start()
        except Exception as exc:
            raise DockerManagerError(str(exc)) from exc

    def stop_container(self, *, instance):
        try:
            container = self.client.containers.get(instance.container_name)
            container.stop()
        except Exception as exc:
            raise DockerManagerError(str(exc)) from exc

    def restart_container(self, *, instance):
        try:
            container = self.client.containers.get(instance.container_name)
            container.restart()
        except Exception as exc:
            raise DockerManagerError(str(exc)) from exc

    def delete_container(self, *, instance):
        """Remove the instance container. The persistent volume is retained by
        default; a Retain/Delete data option arrives in Sprint 6 (VS-043)."""
        try:
            container = self.client.containers.get(instance.container_name)
            container.remove(force=True)
        except docker.errors.NotFound:
            # Already gone (removed externally) — nothing to do.
            pass
        except Exception as exc:
            raise DockerManagerError(str(exc)) from exc

    def remove_volume(self, *, name):
        """Remove a named data volume (VS-043 — delete data option). Missing
        volumes are tolerated (already removed)."""
        try:
            volume = self.client.volumes.get(name)
            volume.remove(force=True)
        except docker.errors.NotFound:
            pass
        except Exception as exc:
            raise DockerManagerError(str(exc)) from exc


# Module-level singleton — services import this rather than instantiating
# DockerManager directly, so it stays mockable in tests
# (06_Backend_Architecture.md Section 17).
docker_manager = DockerManager()

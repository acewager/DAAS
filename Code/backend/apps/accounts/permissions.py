"""Role-based permission helpers for protected endpoints."""
from rest_framework.permissions import BasePermission

from .models import UserRole


class _BaseRolePermission(BasePermission):
    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role in self.allowed_roles


class IsAdminRole(_BaseRolePermission):
    allowed_roles = (UserRole.ADMIN, UserRole.SUPER_ADMIN)


class IsSuperAdminRole(_BaseRolePermission):
    allowed_roles = (UserRole.SUPER_ADMIN,)

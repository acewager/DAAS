"""User accounts and role management."""
import uuid

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UserRole(models.TextChoices):
	USER = "USER", "User"
	ADMIN = "ADMIN", "Admin"
	SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"


class CustomUserManager(UserManager):
	"""Manager that creates users with email normalization and roles."""

	use_in_migrations = True

	def _create_user(self, username, email, password, **extra_fields):
		if not username:
			raise ValueError("The username must be set.")
		if not email:
			raise ValueError("The email must be set.")

		email = self.normalize_email(email)
		user = self.model(username=username, email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, username, email=None, password=None, **extra_fields):
		extra_fields.setdefault("is_staff", False)
		extra_fields.setdefault("is_superuser", False)
		extra_fields.setdefault("role", UserRole.USER)
		return self._create_user(username, email, password, **extra_fields)

	def create_superuser(self, username, email=None, password=None, **extra_fields):
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)
		extra_fields.setdefault("role", UserRole.SUPER_ADMIN)

		if extra_fields.get("is_staff") is not True:
			raise ValueError("Superuser must have is_staff=True.")
		if extra_fields.get("is_superuser") is not True:
			raise ValueError("Superuser must have is_superuser=True.")

		return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
	"""Platform user with UUID primary key and role support."""

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	email = models.EmailField(unique=True)
	role = models.CharField(
		max_length=20,
		choices=UserRole.choices,
		default=UserRole.USER,
	)

	objects = CustomUserManager()

	def __str__(self) -> str:
		return self.username

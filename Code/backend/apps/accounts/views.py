"""Authentication API views."""
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from services.authentication import AuthenticationService

from .throttles import LoginRateThrottle, RegisterRateThrottle
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"success": True, "message": "CSRF cookie set.", "data": {}})


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = AuthenticationService.register_user(
            username=serializer.validated_data["username"],
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        login(request, user)

        return Response(
            {
                "success": True,
                "message": "Account created successfully.",
                "data": {"user": UserSerializer(user).data},
            },
            status=201,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        user = AuthenticationService.authenticate_user(
            username=username,
            password=serializer.validated_data["password"],
        )
        if user is None:
            AuthenticationService.record_failed_login(username)
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": "Invalid username or password.",
                    },
                },
                status=401,
            )

        login(request, user)
        AuthenticationService.record_login(user)
        return Response(
            {
                "success": True,
                "message": "Logged in successfully.",
                "data": {"user": UserSerializer(user).data},
            }
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        AuthenticationService.record_logout(request.user)
        logout(request)
        return Response({"success": True, "message": "Logged out successfully.", "data": {}})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "success": True,
                "message": "Current user retrieved successfully.",
                "data": {"user": UserSerializer(request.user).data},
            }
        )

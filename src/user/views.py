from django.contrib.auth import get_user_model
from rest_framework import generics, status, mixins, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from user.models import UserFollowing
from user.permissions import IsAdminOrIfAuthenticatedReadOnly, IsOwnerOrAdmin
from user.serializers import (
    MyTokenObtainPairSerializer,
    UserSerializer,
    UserListSerializer,
    FollowingSerializer,
    FollowersSerializer,
)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        data = serializer.data
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class LogoutUserView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response(
                {"error": "Invalid token or token expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = get_user_model().objects.all()
    serializer_class = UserListSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsOwnerOrAdmin]
        else:
            permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):

        username = self.request.GET.get("username")
        location = self.request.GET.get("location")

        queryset = self.queryset
        if username:
            queryset = queryset.filter(username__icontains=username)
        if location:
            queryset = queryset.filter(location__icontains=location)
        return queryset.distinct()


class FollowingUsersViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = FollowingSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_authenticated:
            queryset = queryset.get(email=self.request.user)
            return queryset.following.all()
        else:
            return queryset.none()


class FollowersUsersViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = FollowersSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_authenticated:
            queryset = queryset.get(email=self.request.user)
            return queryset.followers.all()
        else:
            return queryset.none()

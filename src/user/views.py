from django.contrib.auth import get_user_model
from rest_framework import generics, status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from user.models import UserFollowing, Post
from user.permissions import IsAdminOrIfAuthenticatedReadOnly, IsOwnerOrAdmin
from user.serializers import (
    MyTokenObtainPairSerializer,
    UserSerializer,
    UserListSerializer,
    FollowingListSerializer,
    FollowersListSerializer,
    UserUpdateSerializer,
    FollowingSerializer,
    PostCreateUpdateSerializer,
    PostListSerializer,
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

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return UserListSerializer
        return UserUpdateSerializer


class FollowingUsersViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = FollowingListSerializer
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
    serializer_class = FollowersListSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_authenticated:
            queryset = queryset.get(email=self.request.user)
            return queryset.followers.all()
        else:
            return queryset.none()


class FollowCreateDestroyViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    serializer_class = FollowingSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_queryset(self):
        return UserFollowing.objects.filter(user_id=self.request.user)

    def post(self, request, *args, **kwargs):
        following_user = get_object_or_404(get_user_model(), id=self.kwargs.get("pk"))

        if request.user == following_user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if UserFollowing.objects.filter(
            user_id=request.user, following_user_id=following_user
        ).exists():
            return Response({"detail": "Already following."}, status=400)

        data = {"following_user_id": following_user.id}
        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user_id=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        following_user = get_object_or_404(get_user_model(), id=self.kwargs.get("pk"))
        instance = self.get_queryset().filter(following_user_id=following_user).first()
        if not instance:
            return Response({"detail": "You are not following this user."}, status=404)
        instance.delete()
        return Response(
            {"detail": "Unfollowed successfully."}, status=status.HTTP_204_NO_CONTENT
        )


class PostListCreateUpdateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Post.objects.all()
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            print(Post.objects.all())
            return PostListSerializer
        return PostCreateUpdateSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsOwnerOrAdmin]
        else:
            permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        hashtag = self.request.GET.get("hashtag")

        if hashtag:
            return Post.objects.filter(hashtag=hashtag)
        else:
            return Post.objects.all()

    @action(detail=True, methods=["post"])
    def toggle_like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)
            return Response({"detail": "Unliked"}, status=status.HTTP_200_OK)
        else:
            post.likes.add(user)
            return Response({"detail": "Liked"}, status=status.HTTP_200_OK)

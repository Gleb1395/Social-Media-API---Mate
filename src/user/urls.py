from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.views import (
    CreateUserView,
    UserViewSet,
    LogoutUserView,
    FollowingUsersViewSet,
    FollowersUsersViewSet,
    FollowCreateDestroyViewSet,
    PostListCreateUpdateDestroyViewSet,
)

router = routers.DefaultRouter()
router.register("users", UserViewSet)
router.register("follow", FollowCreateDestroyViewSet, "follow")
router.register("followings", FollowingUsersViewSet, basename="followings")
router.register("followers", FollowersUsersViewSet, basename="followers")

router.register("posts", PostListCreateUpdateDestroyViewSet, basename="posts")


urlpatterns = [
    path("", include(router.urls)),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", CreateUserView.as_view(), name="register"),
    path("logout/", LogoutUserView.as_view(), name="logout"),
]
app_name = "user"

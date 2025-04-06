from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.models import UserFollowing


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = get_user_model().USERNAME_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)
        return data


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "password2",
            "is_staff",
            "phone_number",
            "username",
        )
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password != password2:
            raise serializers.ValidationError("passwords don't match")
        attrs.pop("password2")
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "username",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "phone_number",
            "bio",
            "profile_image",
            "location",
        )


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "username",
            "profile_image",
            "location",
            "phone_number",
            "bio",
            "profile_picture",
        )


class UserShortsSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "username",
        )


class FollowingListSerializer(serializers.ModelSerializer):
    following_user_id = UserShortsSerializer(read_only=True)

    class Meta:
        model = UserFollowing
        fields = ("following_user_id",)


class FollowersListSerializer(serializers.ModelSerializer):
    user_id = UserShortsSerializer(read_only=True)

    class Meta:
        model = UserFollowing
        fields = ("user_id",)


class FollowingSerializer(serializers.ModelSerializer):
    user_id = UserShortsSerializer(read_only=True)

    class Meta:
        model = UserFollowing
        fields = (
            "id",
            "user_id",
            "following_user_id",
            "created",
        )
        read_only_fields = ("id", "user_id", "created")

    def validate(self, attrs):
        request_user = self.context["request"].user
        following_user = attrs["following_user_id"]

        if request_user == following_user:
            raise serializers.ValidationError("You can't follow yourself")
        return attrs

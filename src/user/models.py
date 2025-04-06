from datetime import timezone, datetime

from django.apps import apps
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """
    Custom user manager for creating regular and super users using email.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _("email address"),
        blank=True,
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    phone_number = models.CharField(
        _("phone number"),
        max_length=15,
        blank=True,
        null=True,
    )
    bio = models.TextField(blank=True, null=True)

    profile_image = models.ImageField(upload_to="profile_image", blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email


class UserFollowing(models.Model):
    """
    Model to represent user-to-user following relationships.
    """

    user_id = models.ForeignKey(
        "User",
        related_name="following",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    following_user_id = models.ForeignKey(
        "User",
        related_name="followers",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "following_user_id"], name="unique_followers"
            )
        ]

        ordering = ["-created"]

    def __str__(self):
        return f"{self.user_id} {self.following_user_id}"


class Post(models.Model):
    """
    Model representing a user-created post with content, image, and hashtags.
    """

    author = models.ForeignKey("User", on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to="post_image", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(
        "User",
        related_name="likes",
        blank=True,
    )
    is_published = models.BooleanField(default=False)
    hashtag = models.ManyToManyField("Hashtag", blank=True, related_name="posts")

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")

    def __str__(self):
        return f"Post {self.id}"


class Hashtag(models.Model):
    """
    Model representing a unique hashtag for categorizing posts.
    """

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = _("hashtag")
        verbose_name_plural = _("hashtags")

    def __str__(self):
        return self.name

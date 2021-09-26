from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from yamdb.models import (Category, Comment, ConfirmationCode, Genre, Review,
                          Title)

CustomUser = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "username",
            "bio",
            "email",
            "role",
        )


def authenticate(password=None, **kwargs):
    email = kwargs.get("email")
    confirmation_code = kwargs.get("confirmation_code")
    if email is None or confirmation_code is None:
        return None
    try:
        user = CustomUser._default_manager.get_by_natural_key(email)
    except CustomUser.DoesNotExist:
        # Run the default password hasher once to reduce the timing
        # difference between an existing and a nonexistent user (#20760).
        CustomUser().set_password(password)
    else:
        if not ConfirmationCode.objects.filter(user=user).exists():
            return None
        confirmation_code_obj = user.confirmation_code
        if (
            confirmation_code_obj.code == confirmation_code
            and user_can_authenticate(user)
        ):
            confirmation_code_obj.delete()
            return user


def user_can_authenticate(user):
    is_active = getattr(user, "is_active", None)
    return is_active or is_active is None


class EmailTokenObtainPairSerializer(serializers.Serializer):
    default_error_messages = {
        "no_active_account": _(
            "No active account found with the given credentials"
        )
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["confirmation_code"] = serializers.CharField(required=True)
        self.fields["email"] = serializers.EmailField(required=True)

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        authenticate_kwargs = {
            "email": attrs["email"],
            "confirmation_code": attrs["confirmation_code"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        data = {}
        refresh = self.get_token(self.user)
        data["token"] = str(refresh.access_token)
        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category
        lookup_field = "slug"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre
        lookup_field = "slug"


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(
        required=False,
        read_only=False,
    )
    genre = GenreSerializer(
        many=True,
        required=False,
        read_only=False,
    )
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "category",
            "genre",
            "description",
        )
        optional_fields = ["year", "category", "genre", "description"]
        model = Title


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        required=False, slug_field="slug", queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        required=False,
        slug_field="slug",
        many=True,
        queryset=Genre.objects.all(),
    )

    class Meta:
        fields = ("id", "name", "year", "category", "genre", "description")
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field="username",
        read_only=True,
    )

    def validate(self, data):
        request = self.context["request"]
        title_id = self.context["view"].kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        if request.method == "POST":
            if Review.objects.filter(
                title=title, author=request.user
            ).exists():
                raise ValidationError("Only one review is allowed")
        return data

    class Meta:
        model = Review
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(slug_field="text", read_only=True)
    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True
    )

    class Meta:
        fields = "__all__"
        model = Comment

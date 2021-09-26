from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filter
from rest_framework import filters, mixins, status, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenViewBase

from yamdb.filters import TitleFilter
from yamdb.models import Category, ConfirmationCode, Genre, Review, Title
from yamdb.permissions import IsAdmin, ReviewAndCommentPermissions
from yamdb.serializers import (CategorySerializer, CommentSerializer,
                               EmailTokenObtainPairSerializer, GenreSerializer,
                               ReviewSerializer, TitleCreateUpdateSerializer,
                               TitleSerializer, UserSerializer)

CustomUser = get_user_model()


class Pagination(LimitOffsetPagination):
    default_limit = 10
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination
    permission_classes = [IsAdmin]
    lookup_field = "username"


class RetrieveUpdateMixin(mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    """
    Миксин обеспечивает методы `retrieve()`, `update()`,
    `partial_update()`.
    """

    pass


class UserMeView(viewsets.GenericViewSet, RetrieveUpdateMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        obj = self.request.user
        self.check_object_permissions(self.request, obj)
        return obj


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if email is None:
            return Response(
                data={"email": "This field is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not CustomUser.objects.filter(email=email).exists():
            CustomUser.objects.create_user(username=email, email=email)

        user = CustomUser.objects.get(email=email)

        if ConfirmationCode.objects.filter(user=user).exists():
            confirmation_code_obj = ConfirmationCode.objects.get(user=user)
            confirmation_code_obj.delete()

        confirmation_code_obj = ConfirmationCode(user=user)
        confirmation_code_obj.save()

        user.email_user(
            subject="Код подверждения",
            message=f"Ваш код подверждения - {confirmation_code_obj.code}",
            from_email="auth@yamdb.org",
        )
        return Response({"email": email}, status=status.HTTP_200_OK)


class EmailTokenObtainPairView(TokenViewBase):
    serializer_class = EmailTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AvailableMethodsViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CategoryViewSet(AvailableMethodsViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = Pagination
    lookup_field = "slug"
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "name",
    ]

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class GenreViewSet(AvailableMethodsViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = Pagination
    lookup_field = "slug"
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "name",
    ]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    pagination_class = Pagination
    permission_classes = [AllowAny]
    filter_backends = [filter.DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TitleSerializer
        return TitleCreateUpdateSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ReviewAndCommentPermissions,)
    pagination_class = Pagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        context.update({'title': title})
        return context

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (ReviewAndCommentPermissions,)
    pagination_class = Pagination

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)

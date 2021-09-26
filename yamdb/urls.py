from django.contrib.auth import get_user_model
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from yamdb.views import (CategoryViewSet, CommentViewSet,
                         EmailTokenObtainPairView, GenreViewSet, RegisterView,
                         ReviewViewSet, TitleViewSet, UserMeView, UserViewSet)

CustomUser = get_user_model()

router_v1 = DefaultRouter()
router_v1.register("users", UserViewSet)
router_v1.register("titles", TitleViewSet)
router_v1.register("genres", GenreViewSet)
router_v1.register("categories", CategoryViewSet)
router_v1.register(
    r'titles/(?P<title_id>[\d]+)/reviews',
    ReviewViewSet,
    basename='review',
)
router_v1.register(
    r'titles/(?P<title_id>[\d]+)/reviews/(?P<review_id>[\d]+)/comments',
    CommentViewSet,
    basename='comment',
)


urlpatterns = [
    path(
        "v1/auth/email/",
        RegisterView.as_view(),
    ),
    path(
        "v1/token/",
        EmailTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "v1/users/me/",
        UserMeView.as_view({"get": "retrieve", "patch": "partial_update"}),
    ),
    path(
        "v1/",
        include(router_v1.urls),
    ),
]

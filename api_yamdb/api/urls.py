from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (
    SignUpAPIView,
    TokenAccessObtainView,
    UserViewSet,
    CategoryViewSet,
    TitleViewSet,
    GenreViewSet,
)

router_v1 = SimpleRouter()

router_v1.register(r'users', UserViewSet)
router_v1.register(r'titles', TitleViewSet, basename='title')
router_v1.register(r'genres', GenreViewSet, basename='genre')
router_v1.register(r'categories', CategoryViewSet, basename='category')


auth_endpoints = [
    path('signup/', SignUpAPIView.as_view(), name='signup'),
    path('token/', TokenAccessObtainView.as_view(), name='access_token'),
]


urlpatterns = [
    path('v1/auth/', include(auth_endpoints)),
    path(
        'v1/users/me/',
        UserViewSet.as_view(
            {'get': 'current_user_data', 'patch': 'current_user_data'}
        ),
        name='users_me',
    ),
    path('v1/', include(router_v1.urls)),
]

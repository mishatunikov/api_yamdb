from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, SignUpAPIView, TitleViewSet,
                       TokenAccessObtainView, UserViewSet)

router_v1 = SimpleRouter()

router_v1.register('users', UserViewSet)
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment',
)


auth_endpoints = [
    path('signup/', SignUpAPIView.as_view(), name='signup'),
    path('token/', TokenAccessObtainView.as_view(), name='access_token'),
]


urlpatterns = [
    path('v1/auth/', include(auth_endpoints)),
    path(
        'v1/users/me/',
        UserViewSet.as_view({'get': 'me', 'patch': 'me_update'}),
        name='users_me',
    ),
    path('v1/', include(router_v1.urls)),
]

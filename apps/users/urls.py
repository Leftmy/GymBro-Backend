from django.urls import path
from .views import RegisterView, LoginView, UserView, UserSearchAPIView
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path("search/", UserSearchAPIView.as_view(), name="search-users"),
    path('auth/register/', RegisterView.as_view(), name='register-user'),
    path('auth/login/', LoginView.as_view(), name='login-user'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserView.as_view(), name='manage-user')
]
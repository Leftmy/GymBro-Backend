from django.urls import path
from .views import RegisterView, LoginView, UserView, UserSearchAPIView
urlpatterns = [
    path("search/", UserSearchAPIView.as_view(), name="search-users"),
    path('auth/register/', RegisterView.as_view(), name='register-user'),
    path('auth/login/', LoginView.as_view(), name='login-user'),
    path('me/', UserView.as_view(), name='manage-user')
]
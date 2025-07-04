from django.urls import path
from accounts.views import AdminSignUpView, UserCreateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import PasswordResetView, PasswordResetConfirmView, ChangePasswordView, UserProfileUpdateView, UserProfileView, UserListView, MyprofileUpdateView

urlpatterns = [
    path('signup/admin/', AdminSignUpView.as_view(), name='admin-signup'),
    path('users/add/', UserCreateView.as_view(), name='user-create'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refersh'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset_form'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-change/', ChangePasswordView.as_view(), name='password-change'),
    path('change-profile/<int:pk>/', UserProfileUpdateView.as_view(), name='change-profile'),
    path('profile-user/', UserProfileView.as_view(), name='profile-user'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('update-profile/', MyprofileUpdateView.as_view(), name='update-profile-user')
]

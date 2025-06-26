from rest_framework import generics, permissions, status
from accounts.models import CustomUser
from accounts.serializers import UserSerializer, PasswordResetConfirmSerializer, AdminUserSerializer
from .permissions import IsAdminOrManagerCanAddEmployee, IsAdminOrManager
from .enums import RoleChoices
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .utils import send_password_reset_email, get_tokens_for_user
from rest_framework.exceptions import PermissionDenied

class AdminSignUpView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        self.user = serializer.save(role=RoleChoices.ADMIN)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        tokens = get_tokens_for_user(self.user)
        response.data.update(tokens)
        return response

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManagerCanAddEmployee]

    def perform_create(self, serializer):
        self.user = serializer.save()
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        tokens = get_tokens_for_user(self.user)
        response.data.update(tokens)
        return response
        
class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email is required.'}, status=400)
        try:
            user = CustomUser.objects.get(email=email)
            send_password_reset_email(user)  
        except CustomUser.DoesNotExist:
            pass  
        return Response({'detail': 'If the email exists, a reset link has been sent.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        new_password = serializer.validated_data['password']
        user.set_password(new_password)
        user.save()

        tokens = get_tokens_for_user(user)
        user_data = UserSerializer(user).data

        return Response({
            'detail': 'Password has been set successfully.',
            'user': user_data,
            'tokens': tokens
            })

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response({'detail': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if old_password == new_password:
            return Response({'detail':'New password cannot be the same as old Password'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({'detail':'Password has been changed successfully'}, status=status.HTTP_200_OK)
    
class UserProfileUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManager]

    def perform_update(self, serializer):
        updater = self.request.user
        target_user = self.get_object()
        new_role = self.request.data.get('role')

        if updater.role == RoleChoices.MANAGER:
            if target_user.role != RoleChoices.EMPLOYEE:
                raise PermissionDenied("Manager can update only employee")
            if new_role and new_role != RoleChoices.EMPLOYEE:
                raise PermissionDenied("Manager can assign only the employee role")
            
        serializer.save()

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class MyprofileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in [RoleChoices.ADMIN, RoleChoices.MANAGER, RoleChoices.EMPLOYEE]:
            return CustomUser.objects.all()
        return CustomUser.objects.none()
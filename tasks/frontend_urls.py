from django.urls import path
from .views import (login, task_create, task_list, update_status, task_update, signup_admin, create_user, dashboard, profile_user, update_profile, password_reset, 
                    password_reset_confirm, user_list, user_update, password_change, task_details, task_attachfile, task_report, user_chat)

urlpatterns = [
    path('login/', login, name="login"),
    path('task_create/', task_create, name="task_create"),
    path('task_list/', task_list, name="task_list"),
    path('update_status/', update_status, name="status_update"),
    path('task_update/', task_update, name="task_update"),
    path('signUp/', signup_admin, name="singup-admin"),
    path('create_user/', create_user, name="create-user"),
    path('user_list/', user_list, name="user_list"),
    path('user_update/', user_update, name="user_update"),
    path('dashboard/', dashboard, name="dashboard"),
    path('user_profile/', profile_user, name="user-profile"),
    path('update_profile/', update_profile, name='user-update-profile'),
    path('password_reset/', password_reset, name="password-reset-email"),
    path('password_reset_confirm/', password_reset_confirm, name="password-reset-confirm-email"),
    path('password_change/', password_change, name="password-change"),
    path('task_detail/', task_details, name="task-detail"),
    path('attachfile/', task_attachfile, name="attachfile-in-task"),
    path('task_report/', task_report, name="task_report"),
    path('user_chat/', user_chat, name="user_chat"),
]
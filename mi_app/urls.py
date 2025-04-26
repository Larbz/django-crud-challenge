# mi_app/urls.py
from django.urls import path
from .views import ProjectView, UserList, UserDeleteView, UserRegisterView, TaskView,DeleteProjectView, DeleteTaskView, UpdateProjectView, UpdateTaskView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('projects/', ProjectView.as_view(), name='project-list'),
    path('projects/delete/<int:project_id>/', DeleteProjectView.as_view(), name='delete-project'),
    path('projects/update/<int:project_id>/', UpdateProjectView.as_view(), name='delete-project'),
    path('tasks/', TaskView.as_view(), name='task-list'),
    path('tasks/delete/<int:task_id>/', DeleteTaskView.as_view(), name='delete-task'),
    path('tasks/update/<int:task_id>/', UpdateTaskView.as_view(), name='update-task'),
    path('users/', UserList.as_view(), name='user-list'),
    path('users/register/', UserRegisterView.as_view(), name='user-register'),
    path('users/delete/', UserDeleteView.as_view(),name="user-delete"),
    path('token/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
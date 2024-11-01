from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name = 'home'),
    path('register', views.register, name = 'register'),
    path('user-login', views.user_login, name = 'user-login'),
    path('dashboard', views.dashboard, name = 'dashboard'),
    path('user-logout', views.user_logout, name = 'user-logout'),
    path('create-task', views.createTask, name = 'create-task'),
    path('view-task', views.viewTask, name = 'view-task'),
    path('update-task/<str:pk>/', views.updateTask, name = 'update-task'),
    path('delete-task/<str:pk>/', views.deleteTask, name = 'delete-task'),
    path('create-project', views.createProject, name='create-project'),
    path('view-projects', views.viewProjects, name='view-projects'),
    path('project/<int:project_id>/tasks/', views.viewTasksByProject, name='view-tasks-by-project'),
    path('notification-preferences/', views.notification_preferences, name='notification-preferences'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),

    path('calendar/', views.calendar_view, name='calendar'),
    path('task/<int:pk>/', views.task_detail, name='task-detail'),
]
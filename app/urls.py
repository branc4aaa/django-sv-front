from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('users/', views.all_users, name='all_u'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('Tasks/', views.tasks_view, name='tasks'),
    path('logout/', views.logout_view, name='logout'),
    path('update_task/<int:task_id>/', views.upd_task_view, name='upd_task'),
    path('new_task/', views.newTask_view, name='newTask'),
    path('delete_task/<int:task_id>/', views.delete_task_view, name='delete_task'),
]
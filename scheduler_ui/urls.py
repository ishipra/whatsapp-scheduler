from django.urls import path
from . import views

app_name = 'scheduler_ui'

urlpatterns = [
    path('', views.index, name='index'),
    path('trigger/', views.trigger_action, name='trigger'),
    path('status/', views.status, name='status'),
]

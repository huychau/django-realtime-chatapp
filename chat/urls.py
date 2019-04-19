from django.urls import path


from . import views

urlpatterns = [
    path('', views.index, name='room_index'),
    path('<str:room>/', views.room, name='room'),
]

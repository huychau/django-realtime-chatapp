from django.urls import path


from . import views

urlpatterns = [
    path('<str:room>/', views.room, name='room'),
]

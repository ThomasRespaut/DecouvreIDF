# Créez un fichier urls.py dans l'application "trips"
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('tensorboard/', views.tensorboard_view, name='tensorboard')#,
    #path('tensorboard/status/', views.tensorboard_status, name='tensorboard_status')#,
    #path('tensorboard/stop/', views.stop_tensorboard, name='stop_tensorboard')

]

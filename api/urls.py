from django.urls import path

from . import views
from . import response
from . import videocapture

urlpatterns = [
    path('login', response.getAuth),
    path('video',videocapture.getVideo),
    path('songs',response.get_songs),
  
]


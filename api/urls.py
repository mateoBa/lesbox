__author__ = 'agusx1211'
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^user/login/', views.login, name='create_user'),
    url(r'^user/parties/', views.get_user_parties, name='get user parties'),
    url(r'^user/join/party', views.join_party, name='get user parties'),
    url(r'^user/leave/party', views.leave_party, name='get user parties'),
    url(r'^party/create/', views.create_party, name='create_party'),
    url(r'^party/tracks/update', views.update_tracks, name='set_tracks'),
    url(r'^party/tracks/add', views.add_track, name='set_tracks'),
    url(r'^party/tracks/get', views.get_tracks, name='get_tracks'),
    url(r'^party/tracks/next', views.get_next_track, name='get_tracks'),
    url(r'^party/tracks/del', views.del_all_tracks, name='get_tracks'),
    url(r'^party/track/del/one', views.del_track, name='get_tracks'),
    url(r'^party/getalltracks', views.get_all_tracks, name='get_tracks'),
]
from django.conf.urls import url

from ldn import settings
from .views import *
from django.conf.urls.static import static


urlpatterns= [

# register new user
#     url(r'^register/$', views.register_view),
    url(r'^login/$', login_view, name='userlogin'),
    url(r'^emailverify/$', email_signup_verify),
    url(r'^adminpanel/$', admin_panel_verify, name='adminpanel'),
    url(r'^adminlogin/$', admin_login_verify),
    url(r'^userlogin/$', user_login_verify),
    url(r'^logout/$', user_logout, name='logout'),
    url(r'^userpatients/$', user_patients),
    url(r'^sendpass/$', send_password, name='sendpass'),
    url(r'^dashboard/(?P<tablename>[a-zA-Z]+)/$', dashboard, name='dashboard'),

    # url(r'^confirm/(?P<activation_key>\w+)/', views.register_confirm),


]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
from django.conf.urls import url

from ldn import settings
from .views import *
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [

                  # register new user
                  #     url(r'^register/$', views.register_view),
                  url(r'^login/$', login_view, name='userlogin'),
                  url(r'^signupverify/$', email_signup_verify),
                  url(r'^adminpanel/$', admin_panel_verify, name='adminpanel'),
                  url(r'^adminlogin/$', admin_login_verify),
                  url(r'^loginverify/$', user_login_verify),
                  url(r'^logout/$', user_logout, name='logout'),
                  url(r'^userpatients/$', user_patients),
                  url(r'^sendpass/$', send_password, name='sendpass'),
                  url(r'^graphs/(?P<patientid>[0-9]+)$', graphs, name='graphs'),
                  # url(r'^matplot/(?P<patientid>[0-9]+)$', matplot, name='matplot'),
                  url(r'^dashboard/$', dashboard, name='dashboard'),
                  # url(r'^dash/$', auth_views.login, name='dash'),
                  url(r'^client_token/$', client_token, name='client_token'),
                  url(r'^checkout/$', create_purchase, name='checkout'),
                  url(r'^purchase/$', purchase, name='purchase'),
                  # url(r'^success/$', success, name='success'),
                  url(r'^checkpayment/$', checkpayment, name='checkpayment'),
                  # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                  #     auth_views.password_reset_confirm, name='password_reset_confirm'),
                  url(r'^changepassword/$',
                      changepassword, name='changepassword'),

                  # url(r'^confirm/(?P<activation_key>\w+)/', views.register_confirm),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

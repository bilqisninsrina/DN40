from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_register, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('history/', views.history, name='history'),
    path('beli/<slug:kategori>/', views.buy, name='buy'),
    path('export/pendaftaran.xlsx', views.export_registrations, name='export_registrations'),
    path('auth/sso/', views.sso_start, name='sso_start'),
    path('auth/sso/callback/', views.sso_callback, name='sso_callback'),
]

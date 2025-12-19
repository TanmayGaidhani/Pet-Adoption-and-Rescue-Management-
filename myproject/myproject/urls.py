"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('rescue/', views.rescue_view, name='rescue'),
    path('found-pet/', views.found_pet_view, name='found_pet'),
    path('report-info/', views.report_info_view, name='report_info'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/users/', views.admin_users_view, name='admin_users'),
    path('admin/reports/', views.admin_reports_view, name='admin_reports'),
    
    # API URLs
    path('api/found-pets/', views.get_found_pets_api, name='get_found_pets_api'),
    path('api/rescue-reports/', views.get_rescue_reports_api, name='get_rescue_reports_api'),
    path('api/admin/stats/', views.admin_stats_api, name='admin_stats_api'),
    path('api/admin/pending-reports/', views.admin_pending_reports_api, name='admin_pending_reports_api'),
    path('api/admin/approve-report/', views.admin_approve_report_api, name='admin_approve_report_api'),
    path('api/admin/users-stats/', views.admin_users_stats_api, name='admin_users_stats_api'),
    path('api/admin/users/', views.admin_users_api, name='admin_users_api'),
    path("send-otp/", views.send_otp, name="send_otp"),
    
    # AI Chatbot API
    path('api/chat/', views.chat_api, name='chat_api')

]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

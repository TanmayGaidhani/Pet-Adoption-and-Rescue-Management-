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
    # Custom Admin URLs (MUST come before Django admin)
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/users/', views.admin_users_view, name='admin_users'),
    path('admin/reports/', views.admin_reports_view, name='admin_reports'),
    path('admin/adoption/', views.admin_adoption_view, name='admin_adoption'),
    path('admin/chat/', views.admin_chat_view, name='admin_chat'),
    path('admin/settings/', views.admin_settings_view, name='admin_settings'),
    path('admin/ml-matching/', views.admin_ml_matching_view, name='admin_ml_matching'),
    
    # Django Admin (MUST come after custom admin URLs)
    path('admin/', admin.site.urls),
    
    # Main URLs
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('rescue/', views.rescue_view, name='rescue'),
    path('found-pet/', views.found_pet_view, name='found_pet'),
    path('report-info/', views.report_info_view, name='report_info'),
    
    # Adoption URLs
    path('adoption/', views.adoption_view, name='adoption'),
    path('view-updates/', views.view_updates_view, name='view_updates'),
    path('community-comments/', views.community_comments_view, name='community_comments'),
    path('profile/', views.user_profile_view, name='user_profile'),
    
    # API URLs
    path('api/found-pets/', views.get_found_pets_api, name='get_found_pets_api'),
    path('api/rescue-reports/', views.get_rescue_reports_api, name='get_rescue_reports_api'),
    path('api/admin/stats/', views.admin_stats_api, name='admin_stats_api'),
    path('api/admin/pending-reports/', views.admin_pending_reports_api, name='admin_pending_reports_api'),
    path('api/admin/approve-report/', views.admin_approve_report_api, name='admin_approve_report_api'),
    path('api/admin/users-stats/', views.admin_users_stats_api, name='admin_users_stats_api'),
    path('api/admin/users/', views.admin_users_api, name='admin_users_api'),
    path('api/admin/delete-user/', views.admin_delete_user_api, name='admin_delete_user_api'),
    path('api/pet-chat/send/', views.pet_chat_send_message_api, name='pet_chat_send_message_api'),
    path('api/pet-chat/messages/<str:report_id>/', views.pet_chat_get_messages_api, name='pet_chat_get_messages_api'),
    path('api/admin/chat-stats/', views.admin_chat_stats_api, name='admin_chat_stats_api'),
    path('api/admin/chat-list/', views.admin_chat_list_api, name='admin_chat_list_api'),
    path('api/admin/chat-messages/<str:report_id>/', views.admin_chat_messages_api, name='admin_chat_messages_api'),
    path('api/admin/send-chat-message/', views.admin_send_chat_message_api, name='admin_send_chat_message_api'),
    path('api/admin/close-chat/', views.admin_close_chat_api, name='admin_close_chat_api'),
    path("send-otp/", views.send_otp, name="send_otp"),
    
    # Adoption API URLs
    path('api/adoption-pets/', views.get_adoption_pets_api, name='get_adoption_pets_api'),
    path('api/adoption-request/', views.submit_adoption_request_api, name='submit_adoption_request_api'),
    path('api/admin/adoption-pets/', views.admin_adoption_pets_api, name='admin_adoption_pets_api'),
    path('api/admin/add-adoption-pet/', views.admin_add_adoption_pet_api, name='admin_add_adoption_pet_api'),
    path('api/admin/adoption-requests/', views.admin_adoption_requests_api, name='admin_adoption_requests_api'),
    path('api/admin/adoption-action/', views.admin_adoption_action_api, name='admin_adoption_action_api'),
    
    # AI Chatbot API
    path('api/chat/', views.chat_api, name='chat_api'),
    
    # User Requests API
    path('api/user-requests/', views.get_user_requests_api, name='get_user_requests_api'),
    
    # Comment System API
    path('api/comments/', views.get_comments_api, name='get_comments_api'),
    path('api/comments/post/', views.post_comment_api, name='post_comment_api'),
    
    # User Profile API
    path('api/profile/stats/', views.user_profile_stats_api, name='user_profile_stats_api'),
    path('api/profile/activity/', views.user_profile_activity_api, name='user_profile_activity_api'),
    path('api/profile/member-since/', views.user_profile_member_since_api, name='user_profile_member_since_api'),
    path('api/profile/update/', views.user_profile_update_api, name='user_profile_update_api'),
    path('api/profile/settings/', views.user_profile_settings_api, name='user_profile_settings_api'),
    path('api/profile/delete/', views.user_profile_delete_api, name='user_profile_delete_api'),
    
    # User Notification API
    path('api/user/notifications/', views.user_notifications_api, name='user_notifications_api'),
    path('api/user/notifications/mark-read/', views.mark_notifications_read_api, name='mark_notifications_read_api'),
    
    # Chat History API
    path('api/chat-history/', views.get_chat_history_api, name='get_chat_history_api'),
    path('api/chat-history/clear/', views.clear_chat_history_api, name='clear_chat_history_api'),
    
    # Simple ML Test
    path('api/simple-ml-test/', views.simple_ml_test_api, name='simple_ml_test_api'),
    path('api/test-pet-matching/', views.test_pet_matching_api, name='test_pet_matching_api'),
    
    # Admin ML Matching API URLs (page URL moved to top)
    path('api/admin/reports-for-matching/', views.admin_get_reports_for_matching_api, name='admin_get_reports_for_matching_api'),
    path('api/admin/run-ml-match/', views.admin_run_ml_match_api, name='admin_run_ml_match_api'),
    path('api/admin/match-results/', views.admin_get_match_results_api, name='admin_get_match_results_api'),
    path('api/admin/match-action/', views.admin_match_action_api, name='admin_match_action_api'),
    path('api/admin/batch-ml-analysis/', views.admin_batch_ml_analysis_api, name='admin_batch_ml_analysis_api'),
    
    # Admin Settings API URLs
    path('api/admin/settings/', views.admin_settings_api, name='admin_settings_api'),
    path('api/admin/settings/save/', views.admin_settings_save_api, name='admin_settings_save_api'),
    path('api/admin/settings/reset/', views.admin_settings_reset_api, name='admin_settings_reset_api'),
    path('api/admin/settings/export/', views.admin_settings_export_api, name='admin_settings_export_api'),
    
    # Admin Reports Management API URLs
    path('api/admin/reports/stats/', views.admin_reports_stats_api, name='admin_reports_stats_api'),
    path('api/admin/reports/all/', views.admin_all_reports_api, name='admin_all_reports_api'),
    path('api/admin/reports/delete/', views.admin_delete_report_api, name='admin_delete_report_api'),

]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

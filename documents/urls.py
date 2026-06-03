from django.contrib import admin
from django.urls import path
from documents import views as doc_views
from django.contrib.auth import views as auth_views
from . import views 
from django.views.generic import TemplateView
from .views import health_check
from django.urls import path
from .views import debug_files

urlpatterns = [
    #path('admin/', admin.site.urls),

    # LANDING PAGE (Public - No Login Required)
    # Visitors see this first before logging in
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('health/', health_check, name='health'),
    # DASHBOARD HOME (Redirect after login - requires authentication)
    # Note: Your existing home view will check if user is logged in
    # If not logged in, it should redirect to landing page
    path('home/', doc_views.home, name='home'),
    path('storage-status/', doc_views.storage_status, name='storage_status'),

    # Profile
    path('profile/', doc_views.profile, name='profile'),

    # Dashboards
    path('admin-dashboard/', doc_views.admin_dashboard, name='admin_dashboard'),
    path('staff-dashboard/', doc_views.staff_dashboard, name='staff_dashboard'),
    path('student-dashboard/', doc_views.student_dashboard, name='student_dashboard'),

    # Upload Document
    path('upload/', doc_views.upload_document, name='upload_document'),

    # View Document
    path('debug-files/', debug_files),
    # Share document
    path('share/<int:doc_id>/', doc_views.share_document, name='share_document'),

    # Delete document
    path('delete/<int:doc_id>/', doc_views.delete_document, name='delete_document'),

    # Register
    path('register/', doc_views.register, name='register'),
    
    # Notification
    path('notifications/read/', views.mark_notifications_read, name='mark_read'),

    # Login
    path('login/', doc_views.login_view, name='login'),

    # download document
    path('download/<int:doc_id>/', views.download_document, name='download_document'),
    # preview document (iframe-friendly)
    path('preview/<int:doc_id>/', doc_views.preview_document, name='preview_document'),


    # Logout
    path('logout/', doc_views.logout_view, name='logout'),
    
    # Fetch notifications
    path('notifications/fetch/', views.fetch_notifications, name='fetch_notifications'),

    # Password reset
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
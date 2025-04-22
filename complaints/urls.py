# complaints/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='complaints/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('complain/', views.complaint_form, name='complain'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    path('my-complaints/<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('admin/update-status/<int:complaint_id>/', views.update_status, name='update_status'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
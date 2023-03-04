from django.urls import path
from .views import (render_1_by_1_pixel, render_link_clicked,
                    get_click_tracking_url, get_open_tracking_url,
                    list_recipients, create_recipient, create_app_user,
                    get_analytics_of_email, handle_authorization_code,
                    list_app_users)
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('1by1pixel/<str:email_details>/', render_1_by_1_pixel, name='1by1pixel'),
    path('link-clicked/<str:email_details>/', render_link_clicked, name='link-clicked'),
    path('get_open_tracking_url/', get_open_tracking_url), 
    path('get_click_tracking_url/', get_click_tracking_url), 
    path('list-recipients/', list_recipients),
    path('list-app-users/', list_app_users),
    path('create-recipient/', create_recipient),
    path('create-app-user/', create_app_user),
    path('analytics/<str:sender>/<str:email_campaign_id>/', get_analytics_of_email),
    path('callback-for-azure/', handle_authorization_code),
]

urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

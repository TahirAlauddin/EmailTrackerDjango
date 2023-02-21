from django.urls import path
from .views import (render_1_by_1_pixel, render_link_clicked,
                     get_tracking_url, list_recipients, create_recipient)

urlpatterns = [
    path('1by1pixel/<str:email_details>/', render_1_by_1_pixel, name='1by1pixel'),
    path('link-clicked/<str:email_details>/', render_link_clicked, name='link-clicked'),
    path('get_open_tracking_url/', get_tracking_url), 
    path('get_click_tracking_url/', get_tracking_url), 
    path('list-recipients/', list_recipients),
    path('creat-recipient/', create_recipient),
]

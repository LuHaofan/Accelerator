from django.urls import path

from . import views

app_name = 'ohara'
urlpatterns = [
    path('', views.upload, name = 'upload'),
    path('text_handler/', views.text_handler, name = 'text_handler'),
    path('success/', views.success, name = 'success'),
    path('repeat_entry_warning/<str:fname>/', views.repeat_entry_warning, name = 'repeat_entry_warning'),
    path('return_to_upload/', views.return_to_upload, name = "return_to_upload"),
    path('view_in_notion/', views.view_in_notion, name = "view_in_notion"),
]
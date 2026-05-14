from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='home'),          # 👈 Landing page
    path('upload/', views.upload_resume, name='upload'),  # 👈 Upload page
    path('download/', views.download_report, name='download'),
]
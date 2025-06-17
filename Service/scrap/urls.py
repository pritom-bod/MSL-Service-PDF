from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home' ),
    path('scrape-pdf/', views.scrape_pdf, name='scrape_pdf'),
]

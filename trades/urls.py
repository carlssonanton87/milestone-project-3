from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('trades/', views.trade_list, name='trade_list'),
    path('trades/add/', views.add_trade, name='add_trade'),
    path('trades/edit/<int:pk>/', views.edit_trade, name='edit_trade'),
    path('trades/delete/<int:pk>/', views.delete_trade, name='delete_trade'),
    path('', TemplateView.as_view(template_name="trades/landing.html"), name='landing'),
    path('', views.landing_redirect, name='landing'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('trades/', views.trade_list, name='trade_list'),
    path('trades/add/', views.add_trade, name='add_trade'),
]

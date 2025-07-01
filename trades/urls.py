from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('trades/', views.trade_list, name='trade_list'),
    path('trades/add/', views.add_trade, name='add_trade'),
    path('trades/edit/<int:pk>/', views.edit_trade, name='edit_trade'),
    path('trades/delete/<int:pk>/', views.delete_trade, name='delete_trade'),
]

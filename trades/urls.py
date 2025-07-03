from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('trades/', views.trade_list, name='trade_list'),
    path('trades/add/', views.add_trade, name='add_trade'),
    path('trades/edit/<int:pk>/', views.edit_trade, name='edit_trade'),
    path('trades/delete/<int:pk>/', views.delete_trade, name='delete_trade'),
    path('trades/undo_delete/', views.undo_delete_trade, name='undo_delete_trade'),
    path('', views.landing_redirect, name='landing'),
    path('error/', views.trigger_error),
    path('trades/export/', views.export_trades_csv, name='export_trades'),
    path('trades/import/', views.import_trades_csv, name='import_trades'),

]

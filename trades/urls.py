from django.urls import path, include
from . import views
from django.contrib import admin
from .views import instrument_search
from django.views.generic import TemplateView

urlpatterns = [
    # Landing (redirects to dashboard if logged in)
    path('', views.landing_redirect, name='landing'),
    # Main dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    # CRUD routes
    path('trades/', views.trade_list, name='trade_list'),
    path('trades/add/', views.add_trade, name='add_trade'),
    path('trades/edit/<int:pk>/', views.edit_trade, name='edit_trade'),
    path('trades/delete/<int:pk>/', views.delete_trade, name='delete_trade'),
    path('trades/undo/', views.undo_delete_trade, name='undo_delete_trade'),
    # CSV import/export
    path('trades/export/', views.export_trades_csv, name='export_trades'),
    path('trades/import/', views.import_trades_csv, name='import_trades'),
    # AJAX instrument lookup
    path('api/instruments/', views.instrument_search, name='instrument_search'),
    # Sentry/test error
    path('error/', views.trigger_error, name='trigger_error'),
    path('account/', views.account_view, name='account'),
    path('account/delete_trades/', views.delete_all_trades, name='delete_all_trades'),
    path('account/delete_account/', views.delete_account, name='delete_account'),
]

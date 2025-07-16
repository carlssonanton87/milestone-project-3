from django.contrib import admin
from .models import Trade


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ("instrument", "user", "entry_date", "exit_date", "outcome")
    list_filter = ("outcome", "entry_date")
    search_fields = ("instrument", "notes")

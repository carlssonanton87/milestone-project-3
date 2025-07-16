import os
import csv
import requests
from datetime import date, timedelta
from collections import defaultdict

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import JsonResponse, HttpResponse

from .models import Trade
from .forms import TradeForm, CSVImportForm, CustomUserCreationForm


# Utility view for testing error logging tools (like Sentry)
def trigger_error(request):
    # This view intentionally crashes to test error handling.
    division_by_zero = 1 / 0


# ----------- Account & Profile Management ------------


@login_required
def account_view(request):
    """
    Show the "My Account" page.
    Includes options to:
      - Change password
      - Delete all trades
      - Delete the account entirely
    """
    return render(request, "trades/account.html")


@login_required
def delete_all_trades(request):
    """
    Delete all trades for the logged-in user.
    Used from the My Account page (POST only).
    """
    if request.method == "POST":
        Trade.objects.filter(user=request.user).delete()
        messages.success(request, "All your trades have been deleted.")
    return redirect("account")


@login_required
def delete_account(request):
    """
    Delete both user account and all related trades.
    Logs user out and redirects to landing page.
    """
    if request.method == "POST":
        Trade.objects.filter(user=request.user).delete()
        user = request.user
        auth_logout(request)
        user.delete()
        messages.info(
            request, "Your account and all data have been permanently deleted."
        )
        return redirect("landing")
    return redirect("account")


# ----------- Instrument Search / AJAX Autocomplete ------------


@login_required
def instrument_search(request):
    """
    API endpoint for the trade instrument autocomplete search box.
    Uses AlphaVantage SYMBOL_SEARCH to get real instrument names & symbols.
    """
    term = request.GET.get("term", "").strip()
    suggestions = []
    if term:
        api_key = settings.INSTRUMENT_API_KEY
        resp = requests.get(
            "https://www.alphavantage.co/query",
            params={"function": "SYMBOL_SEARCH", "keywords": term, "apikey": api_key},
            timeout=5,
        )
        if resp.status_code == 200:
            for match in resp.json().get("bestMatches", []):
                sym = match.get("1. symbol", "")
                name = match.get("2. name", "")
                suggestions.append({"label": f"{sym} – {name}", "value": sym})
    return JsonResponse(suggestions, safe=False)


# ----------- Landing & Auth Views ------------


def landing_redirect(request):
    """
    If logged in: go to dashboard.
    If not: show public landing page.
    """
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "trades/landing.html")


def custom_logout(request):
    """
    Log out the user, show a message, and redirect to landing page.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("landing")


def signup_view(request):
    """
    Sign up (register) new user.
    On success: log in user and redirect to dashboard.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)  # Use custom form!
        if form.is_valid():
            form.save()
            messages.success(request, "New user created! You can now log in.")
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


# ----------- Dashboard & Insights ------------


@login_required
def dashboard(request):
    """
    Dashboard view with all trade statistics and date range filtering.
    Shows:
     - total trades, open/closed count, win rate
     - average return, average holding time
     - extra stats: average win hold, win streak, top profit
     - chart data for return% over time (excluding open trades)
    """
    range_filter = request.GET.get("range", "")
    start_param = request.GET.get("start")
    end_param = request.GET.get("end")
    today = date.today()

    trades = Trade.objects.filter(user=request.user)

    # Custom slider range has highest priority
    if start_param and end_param:
        try:
            start_date = date.fromisoformat(start_param)
            end_date = date.fromisoformat(end_param)
            trades = trades.filter(entry_date__range=(start_date, end_date))
            range_filter = "custom"
        except ValueError:
            pass

    # Otherwise check for a preset date filter (week, month, etc)
    elif range_filter:
        if range_filter == "today":
            trades = trades.filter(entry_date=today)
        elif range_filter == "yesterday":
            trades = trades.filter(entry_date=today - timedelta(days=1))
        elif range_filter == "this_week":
            start = today - timedelta(days=today.weekday())
            trades = trades.filter(entry_date__gte=start)
        elif range_filter == "last_week":
            start = today - timedelta(days=today.weekday() + 7)
            end = start + timedelta(days=6)
            trades = trades.filter(entry_date__range=(start, end))
        elif range_filter == "this_month":
            trades = trades.filter(
                entry_date__month=today.month, entry_date__year=today.year
            )
        elif range_filter == "last_month":
            last_month = today.replace(day=1) - timedelta(days=1)
            trades = trades.filter(
                entry_date__month=last_month.month, entry_date__year=last_month.year
            )
        elif range_filter == "this_year":
            trades = trades.filter(entry_date__year=today.year)

    # If nothing else, default to "last 7 days"
    else:
        default_start = today - timedelta(days=6)
        trades = trades.filter(entry_date__range=(default_start, today))
        range_filter = "last_7_days"

    # -- Calculating key statistics for the dashboard --

    total_trades = trades.count()
    wins = trades.filter(outcome="win").count()
    closed_trades = trades.exclude(outcome="open").count()
    open_trades = trades.filter(outcome="open").count()

    win_rate = (wins / closed_trades) * 100 if closed_trades else 0

    return_values = [
        t.return_percent() for t in trades if t.return_percent() is not None
    ]
    avg_return = sum(return_values) / len(return_values) if return_values else 0

    holding_days = [t.holding_days() for t in trades if t.holding_days() is not None]
    avg_holding = sum(holding_days) / len(holding_days) if holding_days else 0

    # Extra: average holding for wins only, win streak, top win
    win_trades = trades.filter(outcome="win").exclude(exit_date__isnull=True)
    if win_trades:
        avg_win_hold = sum(t.holding_days() for t in win_trades) / win_trades.count()
    else:
        avg_win_hold = 0

    # Find the longest win streak
    sorted_trades = trades.order_by("entry_date")
    max_streak = curr_streak = 0
    for t in sorted_trades:
        if t.outcome == "win":
            curr_streak += 1
            max_streak = max(max_streak, curr_streak)
        else:
            curr_streak = 0

    # Top win in terms of raw profit (not %)
    profits = [
        float((t.exit_price - t.entry_price) * t.position_size)
        for t in win_trades
        if t.exit_price is not None
    ]
    top_win = max(profits) if profits else 0

    # Prepare data for the performance chart (average return % per day)
    chart_data = defaultdict(list)
    for t in trades.exclude(outcome="open").order_by("entry_date"):
        rp = t.return_percent()
        if rp is not None:
            chart_data[str(t.entry_date)].append(float(rp))

    chart_labels = []
    chart_returns = []
    for day, returns in chart_data.items():
        chart_labels.append(day)
        chart_returns.append(round(sum(returns) / len(returns), 2))

    context = {
        "total_trades": total_trades,
        "open_trades": open_trades,
        "closed_trades": closed_trades,
        "win_rate": round(win_rate, 2),
        "avg_return": round(avg_return, 2),
        "avg_holding": round(avg_holding, 2),
        "avg_win_hold": round(avg_win_hold, 1),
        "win_streak": max_streak,
        "top_win": round(top_win, 2),
        "range_filter": range_filter,
        "chart_labels": chart_labels,
        "chart_returns": chart_returns,
        "chart_labels_json": chart_labels,
        "chart_returns_json": chart_returns,
    }

    return render(request, "trades/dashboard.html", context)


# ----------- Trade CRUD Views ------------


@login_required
def trade_list(request):
    """
    Show all trades for this user.
    Also passes unique instruments for the filter menu.
    """
    trades = Trade.objects.filter(user=request.user).order_by("-entry_date")
    instruments = (
        trades.values_list("instrument", flat=True).distinct().order_by("instrument")
    )
    return render(
        request,
        "trades/trade_list.html",
        {
            "trades": trades,
            "instruments": instruments,
        },
    )


@login_required
def add_trade(request):
    """
    Add a new trade via form.
    On success, the trade is associated with the current user.
    """
    form = TradeForm(request.POST or None)
    if form.is_valid():
        trade = form.save(commit=False)
        trade.user = request.user
        trade.save()
        messages.success(request, "Trade successfully added.")
        return redirect("trade_list")
    return render(request, "trades/add_trade.html", {"form": form})


@login_required
def edit_trade(request, pk):
    """
    Edit a trade (only if it belongs to the user).
    Uses same template as add.
    """
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    form = TradeForm(request.POST or None, instance=trade)
    if form.is_valid():
        form.save()
        messages.success(request, "Trade updated successfully.")
        return redirect("trade_list")
    return render(request, "trades/add_trade.html", {"form": form})


@login_required
def delete_trade(request, pk):
    """
    Delete a trade, but allow undo (stores the trade data in session for one click).
    """
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    if request.method == "POST":
        # Save trade details to session for "Undo"
        request.session["deleted_trade"] = {
            "instrument": trade.instrument,
            "position_size": str(trade.position_size),
            "entry_price": str(trade.entry_price),
            "exit_price": str(trade.exit_price) if trade.exit_price else "",
            "entry_date": trade.entry_date.isoformat(),
            "exit_date": trade.exit_date.isoformat() if trade.exit_date else "",
            "outcome": trade.outcome,
            "notes": trade.notes,
        }
        trade.delete()
        undo_url = reverse("undo_delete_trade")
        msg = mark_safe(f"Trade deleted. <a href='{undo_url}'>Undo</a>")
        messages.success(request, msg)
        return redirect("trade_list")
    return render(request, "trades/delete_trade.html", {"trade": trade})


@login_required
def undo_delete_trade(request):
    """
    Restore the last deleted trade (if undo was clicked).
    """
    data = request.session.pop("deleted_trade", None)
    if data:
        Trade.objects.create(
            user=request.user,
            instrument=data["instrument"],
            position_size=data["position_size"],
            entry_price=data["entry_price"],
            exit_price=data["exit_price"] or None,
            entry_date=data["entry_date"],
            exit_date=data["exit_date"] or None,
            outcome=data["outcome"],
            notes=data["notes"],
        )
        messages.success(request, "Deletion undone. Trade restored.")
    else:
        messages.warning(request, "No trade to undo.")
    return redirect("trade_list")


# ----------- CSV Import/Export ------------


@login_required
def export_trades_csv(request):
    """
    Download all trades for this user as a CSV file.
    """
    trades = Trade.objects.filter(user=request.user).order_by("entry_date")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="trades.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "instrument",
            "position_size",
            "entry_price",
            "exit_price",
            "entry_date",
            "exit_date",
            "outcome",
            "notes",
        ]
    )
    for t in trades:
        writer.writerow(
            [
                t.instrument,
                t.position_size,
                t.entry_price,
                t.exit_price or "",
                t.entry_date,
                t.exit_date or "",
                t.outcome,
                t.notes or "",
            ]
        )
    return response


@login_required
def import_trades_csv(request):
    """
    Import trades from a user-uploaded CSV.
    Accepts a file, parses rows, and creates new trades for the user.
    """
    form = CSVImportForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        csv_file = form.cleaned_data["file"]
        decoded = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded)
        count = 0
        for row in reader:
            try:
                Trade.objects.create(
                    user=request.user,
                    instrument=row["instrument"],
                    position_size=row["position_size"],
                    entry_price=row["entry_price"],
                    exit_price=row.get("exit_price") or None,
                    entry_date=row["entry_date"],
                    exit_date=row.get("exit_date") or None,
                    outcome=row["outcome"],
                    notes=row.get("notes") or "",
                )
                count += 1
            except Exception:
                continue
        messages.success(request, f"Imported {count} trades successfully.")
        return redirect("trade_list")
    return render(request, "trades/import_trades.html", {"form": form})

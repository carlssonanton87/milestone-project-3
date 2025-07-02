from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from datetime import timedelta, date
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Trade
from .forms import TradeForm

def landing_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, "trades/landing.html")

def trigger_error(request):
    division_by_zero = 1 / 0


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    """
    Displays trading stats, optionally filtered by date presets.
    """
    range_filter = request.GET.get('range', 'all')
    today = date.today()

    # Start with all trades
    trades = Trade.objects.filter(user=request.user)

    # Apply filter presets
    if range_filter == 'today':
        trades = trades.filter(entry_date=today)
    elif range_filter == 'yesterday':
        trades = trades.filter(entry_date=today - timedelta(days=1))
    elif range_filter == 'this_week':
        start = today - timedelta(days=today.weekday())
        trades = trades.filter(entry_date__gte=start)
    elif range_filter == 'last_week':
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=6)
        trades = trades.filter(entry_date__range=(start, end))
    elif range_filter == 'this_month':
        trades = trades.filter(entry_date__month=today.month, entry_date__year=today.year)
    elif range_filter == 'last_month':
        last_month = today.replace(day=1) - timedelta(days=1)
        trades = trades.filter(entry_date__month=last_month.month, entry_date__year=last_month.year)
    elif range_filter == 'this_year':
        trades = trades.filter(entry_date__year=today.year)

    # Optional: date range from slider
    start = request.GET.get('start')
    end = request.GET.get('end')
    if start and end:
       try:
           start_date = date.fromisoformat(start)
           end_date = date.fromisoformat(end)
           trades = trades.filter(entry_date__range=(start_date, end_date))
       except ValueError:
          pass


    # Stats calculation
    total_trades = trades.count()
    wins = trades.filter(outcome='win').count()
    closed_trades = trades.exclude(outcome='open').count()
    open_trades = trades.filter(outcome='open').count()

    win_rate = (wins / closed_trades) * 100 if closed_trades > 0 else 0
    return_values = [t.return_percent() for t in trades if t.return_percent() is not None]
    avg_return = sum(return_values) / len(return_values) if return_values else 0
    holding_days = [t.holding_days() for t in trades if t.holding_days() is not None]
    avg_holding = sum(holding_days) / len(holding_days) if holding_days else 0

    context = {
        'total_trades': total_trades,
        'open_trades': open_trades,
        'closed_trades': closed_trades,
        'win_rate': round(win_rate, 2),
        'avg_return': round(avg_return, 2),
        'avg_holding': round(avg_holding, 2),
        'range_filter': range_filter,
    }

    return render(request, 'trades/dashboard.html', context)




@login_required
def trade_list(request):
    """
    Displays a list of all trades for the logged-in user.
    Sorted by most recent entry date first.
    """
    trades = Trade.objects.filter(user=request.user).order_by('-entry_date')
    return render(request, 'trades/trade_list.html', {'trades': trades})


@login_required
def add_trade(request):
    """
    Displays a form to add a new trade.
    Saves the trade if the form is valid and assigns it to the current user.
    """
    if request.method == 'POST':
        form = TradeForm(request.POST)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.user = request.user
            trade.save()
            messages.success(request, "Trade successfully added.")
            return redirect('trade_list')
    else:
        form = TradeForm()

    return render(request, 'trades/add_trade.html', {'form': form})


@login_required
def edit_trade(request, pk):
    """
    Allows the logged-in user to edit one of their trades.
    """
    trade = get_object_or_404(Trade, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TradeForm(request.POST, instance=trade)
        if form.is_valid():
            form.save()
            messages.success(request, "Trade updated successfully.")
            return redirect('trade_list')
    else:
        form = TradeForm(instance=trade)

    return render(request, 'trades/add_trade.html', {'form': form})


@login_required
def delete_trade(request, pk):
    """
    Confirms and deletes a user's trade if it exists.
    """
    trade = get_object_or_404(Trade, pk=pk, user=request.user)

    if request.method == 'POST':
        trade.delete()
        messages.success(request, "Trade deleted successfully.")
        return redirect('trade_list')

    return render(request, 'trades/delete_trade.html', {'trade': trade})

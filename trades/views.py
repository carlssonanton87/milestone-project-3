import os
import csv
import requests
from datetime import date, timedelta
from collections import defaultdict

from django.shortcuts                import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth            import login, logout
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms      import UserCreationForm
from django.conf                     import settings       # ← must come before using settings
from django.contrib                  import messages
from django.urls                     import reverse
from django.utils.safestring         import mark_safe
from django.http                     import JsonResponse, HttpResponse

from .models import Trade
from .forms  import TradeForm, CSVImportForm


def trigger_error(request):
    # this intentionally raises a ZeroDivisionError so you can test Sentry/etc
    division_by_zero = 1 / 0


@login_required
def account_view(request):
    """
    My Account page:
     - Link to change password
     - Button to delete all trades
     - Button to delete the user account
    """
    return render(request, 'trades/account.html')


@login_required
def delete_all_trades(request):
    if request.method == 'POST':
        # Delete every trade belonging to the user
        Trade.objects.filter(user=request.user).delete()
        messages.success(request, "All your trades have been deleted.")
    return redirect('account')


@login_required
def delete_account(request):
    if request.method == 'POST':
        # First, delete all trades
        Trade.objects.filter(user=request.user).delete()
        # Then, log out & delete the user
        user = request.user
        auth_logout(request)
        user.delete()
        messages.info(request, "Your account and all data have been permanently deleted.")
        return redirect('landing')  # landing_redirect view
    return redirect('account')

@login_required
def instrument_search(request):
    """
    AJAX endpoint for jQuery UI Autocomplete.
    Expects `term` in the query string; returns a list of {label, value}.
    """
    term = request.GET.get('term', '').strip()
    suggestions = []

    if term:
        # read your key at call-time
        api_key = settings.INSTRUMENT_API_KEY
        resp = requests.get(
            'https://www.alphavantage.co/query',
            params={
                'function':  'SYMBOL_SEARCH',
                'keywords':  term,
                'apikey':    api_key
            },
            timeout=5
        )
        if resp.status_code == 200:
            for match in resp.json().get('bestMatches', []):
                sym  = match.get('1. symbol', '')
                name = match.get('2. name', '')
                suggestions.append({
                    'label': f"{sym} – {name}",
                    'value': sym
                })

    return JsonResponse(suggestions, safe=False)


def landing_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, "trades/landing.html")


def custom_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('landing')


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
    Trading dashboard showing stats and optional date filters (presets + slider).
    Defaults to last 7 days if no filter provided.
    """
    range_filter = request.GET.get('range', '')
    start_param  = request.GET.get('start')
    end_param    = request.GET.get('end')
    today        = date.today()

    trades = Trade.objects.filter(user=request.user)

    # 1) Custom slider range wins
    if start_param and end_param:
        try:
            start_date = date.fromisoformat(start_param)
            end_date   = date.fromisoformat(end_param)
            trades     = trades.filter(entry_date__range=(start_date, end_date))
            range_filter = 'custom'
        except ValueError:
            pass

    # 2) Otherwise apply preset filter
    elif range_filter:
        if range_filter == 'today':
            trades = trades.filter(entry_date=today)
        elif range_filter == 'yesterday':
            trades = trades.filter(entry_date=today - timedelta(days=1))
        elif range_filter == 'this_week':
            start = today - timedelta(days=today.weekday())
            trades = trades.filter(entry_date__gte=start)
        elif range_filter == 'last_week':
            start = today - timedelta(days=today.weekday() + 7)
            end   = start + timedelta(days=6)
            trades = trades.filter(entry_date__range=(start, end))
        elif range_filter == 'this_month':
            trades = trades.filter(entry_date__month=today.month,
                                   entry_date__year=today.year)
        elif range_filter == 'last_month':
            last_month = today.replace(day=1) - timedelta(days=1)
            trades = trades.filter(entry_date__month=last_month.month,
                                   entry_date__year=last_month.year)
        elif range_filter == 'this_year':
            trades = trades.filter(entry_date__year=today.year)

    # 3) Fallback: last 7 days
    else:
        default_start = today - timedelta(days=6)
        trades = trades.filter(entry_date__range=(default_start, today))
        range_filter = 'last_7_days'

    # --- Stats ---
    total_trades  = trades.count()
    wins          = trades.filter(outcome='win').count()
    closed_trades = trades.exclude(outcome='open').count()
    open_trades   = trades.filter(outcome='open').count()

    win_rate = (wins / closed_trades) * 100 if closed_trades else 0

    return_values  = [t.return_percent() for t in trades if t.return_percent() is not None]
    avg_return     = sum(return_values) / len(return_values) if return_values else 0

    holding_days   = [t.holding_days() for t in trades if t.holding_days() is not None]
    avg_holding    = sum(holding_days) / len(holding_days) if holding_days else 0

 # ─── New Metrics ───────────────────────────────────

    # 1) Average Win Hold (avg holding_days of only 'win' trades)
    win_trades = trades.filter(outcome='win').exclude(exit_date__isnull=True)
    if win_trades:
        avg_win_hold = sum(t.holding_days() for t in win_trades) / win_trades.count()
    else:
        avg_win_hold = 0

    # 2) Win Streak (longest consecutive sequence of 'win' outcomes in date order)
    sorted_trades = trades.order_by('entry_date')
    max_streak = curr_streak = 0
    for t in sorted_trades:
        if t.outcome == 'win':
            curr_streak += 1
            max_streak = max(max_streak, curr_streak)
        else:
            curr_streak = 0

    # 3) Top Win $ (largest gross profit: (exit_price - entry_price) * position_size)
    profits = [
        float((t.exit_price - t.entry_price) * t.position_size)
        for t in win_trades
        if t.exit_price is not None
    ]
    top_win = max(profits) if profits else 0

    # ────────────────────────────────────────────────────

    # --- Chart data --- (exclude open trades)
    chart_data = defaultdict(list)
    for t in trades.exclude(outcome='open').order_by('entry_date'):
        rp = t.return_percent()
        if rp is not None:
            chart_data[str(t.entry_date)].append(float(rp))

    chart_labels  = []
    chart_returns = []
    for day, returns in chart_data.items():
        chart_labels.append(day)
        chart_returns.append(round(sum(returns) / len(returns), 2))

    context = {
        'total_trades':     total_trades,
        'open_trades':      open_trades,
        'closed_trades':    closed_trades,
        'win_rate':         round(win_rate, 2),
        'avg_return':       round(avg_return, 2),
        'avg_holding':      round(avg_holding, 2),
        'avg_win_hold':    round(avg_win_hold, 1),
        'win_streak':      max_streak,
        'top_win':         round(top_win, 2),
        'range_filter':     range_filter,
        'chart_labels':     chart_labels,
        'chart_returns':    chart_returns,
        'chart_labels_json':  chart_labels,
        'chart_returns_json': chart_returns,
    }

    return render(request, 'trades/dashboard.html', context)


@login_required
def trade_list(request):
    trades = Trade.objects.filter(user=request.user).order_by('-entry_date')
    instruments = (
        trades
        .values_list('instrument', flat=True)
        .distinct()
        .order_by('instrument')
    )
    return render(request, 'trades/trade_list.html', {
        'trades':      trades,
        'instruments': instruments,
    })


@login_required
def add_trade(request):
    form = TradeForm(request.POST or None)
    if form.is_valid():
        trade = form.save(commit=False)
        trade.user = request.user
        trade.save()
        messages.success(request, "Trade successfully added.")
        return redirect('trade_list')
    return render(request, 'trades/add_trade.html', {'form': form})


@login_required
def edit_trade(request, pk):
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    form  = TradeForm(request.POST or None, instance=trade)
    if form.is_valid():
        form.save()
        messages.success(request, "Trade updated successfully.")
        return redirect('trade_list')
    return render(request, 'trades/add_trade.html', {'form': form})


@login_required
def delete_trade(request, pk):
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    if request.method == 'POST':
        request.session['deleted_trade'] = {
            'instrument':    trade.instrument,
            'position_size': str(trade.position_size),
            'entry_price':   str(trade.entry_price),
            'exit_price':    str(trade.exit_price) if trade.exit_price else '',
            'entry_date':    trade.entry_date.isoformat(),
            'exit_date':     trade.exit_date.isoformat() if trade.exit_date else '',
            'outcome':       trade.outcome,
            'notes':         trade.notes,
        }
        trade.delete()

        undo_url = reverse('undo_delete_trade')
        msg = mark_safe(f"Trade deleted. <a href='{undo_url}'>Undo</a>")
        messages.success(request, msg)

        return redirect('trade_list')
    return render(request, 'trades/delete_trade.html', {'trade': trade})


@login_required
def undo_delete_trade(request):
    data = request.session.pop('deleted_trade', None)
    if data:
        Trade.objects.create(
            user          = request.user,
            instrument    = data['instrument'],
            position_size = data['position_size'],
            entry_price   = data['entry_price'],
            exit_price    = data['exit_price'] or None,
            entry_date    = data['entry_date'],
            exit_date     = data['exit_date'] or None,
            outcome       = data['outcome'],
            notes         = data['notes'],
        )
        messages.success(request, "Deletion undone. Trade restored.")
    else:
        messages.warning(request, "No trade to undo.")
    return redirect('trade_list')


@login_required
def export_trades_csv(request):
    trades   = Trade.objects.filter(user=request.user).order_by('entry_date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="trades.csv"'
    writer   = csv.writer(response)
    writer.writerow([
        'instrument','position_size','entry_price','exit_price',
        'entry_date','exit_date','outcome','notes'
    ])
    for t in trades:
        writer.writerow([
            t.instrument, t.position_size, t.entry_price,
            t.exit_price or '', t.entry_date, t.exit_date or '',
            t.outcome, t.notes or '',
        ])
    return response


@login_required
def import_trades_csv(request):
    form = CSVImportForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        csv_file = form.cleaned_data['file']
        decoded  = csv_file.read().decode('utf-8').splitlines()
        reader   = csv.DictReader(decoded)
        count    = 0
        for row in reader:
            try:
                Trade.objects.create(
                    user          = request.user,
                    instrument    = row['instrument'],
                    position_size = row['position_size'],
                    entry_price   = row['entry_price'],
                    exit_price    = row.get('exit_price') or None,
                    entry_date    = row['entry_date'],
                    exit_date     = row.get('exit_date') or None,
                    outcome       = row['outcome'],
                    notes         = row.get('notes') or '',
                )
                count += 1
            except Exception:
                continue
        messages.success(request, f"Imported {count} trades successfully.")
        return redirect('trade_list')
    return render(request, 'trades/import_trades.html', {'form': form})

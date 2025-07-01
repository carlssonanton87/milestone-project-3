from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Trade
from .forms import TradeForm


@login_required
def dashboard(request):
    """
    Displays the main dashboard view with a welcome message.
    Future version will include win rate, return %, and other stats.
    """
    return render(request, 'trades/dashboard.html')


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

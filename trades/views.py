from django.contrib.auth.decorators import login_required
from .models import Trade

@login_required
def trade_list(request):
    # Get all trades belonging to the logged-in user
    trades = Trade.objects.filter(user=request.user).order_by('-entry_date')

    # Send the trades to the template
    return render(request, 'trades/trade_list.html', {'trades': trades})

from django.contrib import messages
from .forms import TradeForm

@login_required
def add_trade(request):
    if request.method == 'POST':
        form = TradeForm(request.POST)
        if form.is_valid():
            # Save the form but don't commit to database yet
            trade = form.save(commit=False)
            trade.user = request.user  # Link the trade to the current user
            trade.save()
            messages.success(request, "Trade successfully added.")
            return redirect('trade_list')
    else:
        form = TradeForm()

    # Render the form on GET or invalid POST
    return render(request, 'trades/add_trade.html', {'form': form})

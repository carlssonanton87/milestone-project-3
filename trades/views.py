from django.contrib.auth.decorators import login_required
from .models import Trade

@login_required
def trade_list(request):
    # Get all trades belonging to the logged-in user
    trades = Trade.objects.filter(user=request.user).order_by('-entry_date')

    # Send the trades to the template
    return render(request, 'trades/trade_list.html', {'trades': trades})

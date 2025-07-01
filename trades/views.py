from django.shortcuts import render

def dashboard(request):
    return render(request, 'trades/dashboard.html')



def trade_list(request):
    return render(request, 'trades/trade_list.html')

def add_trade(request):
    return render(request, 'trades/add_trade.html')


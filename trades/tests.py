from django.test import TestCase
from django.contrib.auth.models import User
from .models import Trade
from datetime import date

class TradeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.trade = Trade.objects.create(
            user=self.user,
            instrument='AAPL',
            position_size=1000.00,
            entry_price=100.00,
            exit_price=110.00,
            entry_date=date(2024, 1, 1),
            exit_date=date(2024, 1, 3),
            outcome='win',
            notes='Test trade'
        )

    def test_return_percent(self):
        """Test the return_percent method returns correct percentage"""
        self.assertAlmostEqual(self.trade.return_percent(), 10.0, places=2)

    def test_holding_days(self):
        """Test the holding_days method returns correct number of days"""
        self.assertEqual(self.trade.holding_days(), 2)

    def test_trade_str_representation(self):
        """Test the __str__ method of the Trade model"""
        self.assertEqual(str(self.trade), "AAPL - 2024-01-01")

    def test_trade_outcome_choices(self):
        """Test the outcome field accepts valid choices"""
        trade = Trade.objects.create(
            user=self.user,
            instrument='GOOG',
            position_size=2000.00,
            entry_price=200.00,
            entry_date=date(2024, 5, 1),
            outcome='open'
        )
        self.assertEqual(trade.outcome, 'open')

    def test_open_trade_return_none(self):
        """Test return_percent and holding_days return None for open trades"""
        trade = Trade.objects.create(
            user=self.user,
            instrument='TSLA',
            position_size=1500.00,
            entry_price=300.00,
            entry_date=date(2024, 6, 1),
            outcome='open'
        )
        self.assertIsNone(trade.return_percent())
        self.assertIsNone(trade.holding_days())

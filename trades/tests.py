from django.test import TestCase
from django.contrib.auth.models import User
from .models import Trade
from datetime import date
from django.urls import reverse     

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


class TradeCRUDPermissionTests(TestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')

        # Create a trade for each
        self.trade1 = Trade.objects.create(
            user=self.user1,
            instrument='ABC',
            position_size=10,
            entry_price=100,
            exit_price=110,
            entry_date=date(2025,1,1),
            exit_date=date(2025,1,2),
            outcome='win',
        )
        self.trade2 = Trade.objects.create(
            user=self.user2,
            instrument='XYZ',
            position_size=5,
            entry_price=50,
            exit_price=45,
            entry_date=date(2025,2,1),
            exit_date=date(2025,2,2),
            outcome='loss',
        )

    def test_trade_list_shows_only_own_trades(self):
        self.client.login(username='user1', password='pass1')
        response = self.client.get(reverse('trade_list'))
        trades = response.context['trades']
        self.assertIn(self.trade1, trades)
        self.assertNotIn(self.trade2, trades)

    def test_create_trade(self):
        self.client.login(username='user1', password='pass1')
        url = reverse('add_trade')
        data = {
            'instrument': 'NEW',
            'position_size': '2.5',
            'entry_price': '20',
            'exit_price': '25',
            'entry_date': '2025-03-01',
            'exit_date': '2025-03-02',
            'outcome': 'win',
            'notes': 'Test',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Trade.objects.filter(user=self.user1, instrument='NEW').exists())

    def test_edit_trade(self):
        self.client.login(username='user1', password='pass1')
        url = reverse('edit_trade', args=[self.trade1.pk])
        data = {
            'instrument': 'ABC-updated',
            'position_size': self.trade1.position_size,
            'entry_price': self.trade1.entry_price,
            'exit_price': self.trade1.exit_price,
            'entry_date': self.trade1.entry_date,
            'exit_date': self.trade1.exit_date,
            'outcome': self.trade1.outcome,
            'notes': 'Updated',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.trade1.refresh_from_db()
        self.assertEqual(self.trade1.instrument, 'ABC-updated')

    def test_delete_trade(self):
        self.client.login(username='user1', password='pass1')
        url = reverse('delete_trade', args=[self.trade1.pk])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Trade.objects.filter(pk=self.trade1.pk).exists())

    def test_cannot_edit_another_users_trade(self):
        self.client.login(username='user1', password='pass1')
        url = reverse('edit_trade', args=[self.trade2.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_another_users_trade(self):
        self.client.login(username='user1', password='pass1')
        url = reverse('delete_trade', args=[self.trade2.pk])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)
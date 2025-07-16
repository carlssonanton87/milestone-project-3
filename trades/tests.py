from django.test import TestCase
from django.contrib.auth.models import User
from .models import Trade
from datetime import date
from django.urls import reverse

# --- Model Tests: Test Trade logic/calculations ---


class TradeModelTests(TestCase):
    def setUp(self):
        # I create a test user and a trade to use for all the tests in this class.
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.trade = Trade.objects.create(
            user=self.user,
            instrument="AAPL",
            position_size=1000.00,
            entry_price=100.00,
            exit_price=110.00,
            entry_date=date(2024, 1, 1),
            exit_date=date(2024, 1, 3),
            outcome="win",
            notes="Test trade",
        )

    def test_return_percent(self):
        """I test that return_percent() calculates correct return."""
        self.assertAlmostEqual(self.trade.return_percent(), 10.0, places=2)

    def test_holding_days(self):
        """I test that holding_days() returns the correct duration (in days)."""
        self.assertEqual(self.trade.holding_days(), 2)

    def test_trade_str_representation(self):
        """I check that __str__ returns the expected trade string."""
        self.assertEqual(str(self.trade), "AAPL - 2024-01-01")

    def test_trade_outcome_choices(self):
        """I test the outcome field accepts valid choices like 'open'."""
        trade = Trade.objects.create(
            user=self.user,
            instrument="GOOG",
            position_size=2000.00,
            entry_price=200.00,
            entry_date=date(2024, 5, 1),
            outcome="open",
        )
        self.assertEqual(trade.outcome, "open")

    def test_open_trade_return_none(self):
        """If a trade is open, return_percent() and holding_days() should return None."""
        trade = Trade.objects.create(
            user=self.user,
            instrument="TSLA",
            position_size=1500.00,
            entry_price=300.00,
            entry_date=date(2024, 6, 1),
            outcome="open",
        )
        self.assertIsNone(trade.return_percent())
        self.assertIsNone(trade.holding_days())


# --- CRUD Permissions: Only owner can edit/delete their trades ---


class TradeCRUDPermissionTests(TestCase):
    def setUp(self):
        # I set up two users and a trade for each
        self.user1 = User.objects.create_user(username="user1", password="pass1")
        self.user2 = User.objects.create_user(username="user2", password="pass2")

        self.trade1 = Trade.objects.create(
            user=self.user1,
            instrument="ABC",
            position_size=10,
            entry_price=100,
            exit_price=110,
            entry_date=date(2025, 1, 1),
            exit_date=date(2025, 1, 2),
            outcome="win",
        )
        self.trade2 = Trade.objects.create(
            user=self.user2,
            instrument="XYZ",
            position_size=5,
            entry_price=50,
            exit_price=45,
            entry_date=date(2025, 2, 1),
            exit_date=date(2025, 2, 2),
            outcome="loss",
        )

    def test_trade_list_shows_only_own_trades(self):
        """When logged in, I should only see my trades, not others'."""
        self.client.login(username="user1", password="pass1")
        response = self.client.get(reverse("trade_list"))
        trades = response.context["trades"]
        self.assertIn(self.trade1, trades)
        self.assertNotIn(self.trade2, trades)

    def test_create_trade(self):
        """I can create a trade and it appears in my list."""
        self.client.login(username="user1", password="pass1")
        url = reverse("add_trade")
        data = {
            "instrument": "NEW",
            "position_size": "2.5",
            "entry_price": "20",
            "exit_price": "25",
            "entry_date": "2025-03-01",
            "exit_date": "2025-03-02",
            "outcome": "win",
            "notes": "Test",
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Trade.objects.filter(user=self.user1, instrument="NEW").exists()
        )

    def test_edit_trade(self):
        """I can edit my own trade and see the updated data."""
        self.client.login(username="user1", password="pass1")
        url = reverse("edit_trade", args=[self.trade1.pk])
        data = {
            "instrument": "ABC-updated",
            "position_size": self.trade1.position_size,
            "entry_price": self.trade1.entry_price,
            "exit_price": self.trade1.exit_price,
            "entry_date": self.trade1.entry_date,
            "exit_date": self.trade1.exit_date,
            "outcome": self.trade1.outcome,
            "notes": "Updated",
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.trade1.refresh_from_db()
        self.assertEqual(self.trade1.instrument, "ABC-updated")

    def test_delete_trade(self):
        """I can delete my own trade and it disappears from the database."""
        self.client.login(username="user1", password="pass1")
        url = reverse("delete_trade", args=[self.trade1.pk])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Trade.objects.filter(pk=self.trade1.pk).exists())

    def test_cannot_edit_another_users_trade(self):
        """I should not be able to edit someone else's trade (should get 404)."""
        self.client.login(username="user1", password="pass1")
        url = reverse("edit_trade", args=[self.trade2.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_another_users_trade(self):
        """I should not be able to delete someone else's trade (should get 404)."""
        self.client.login(username="user1", password="pass1")
        url = reverse("delete_trade", args=[self.trade2.pk])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)


# --- Message Testing: Success/error for CRUD ---


class TradeMessageTests(TestCase):
    def setUp(self):
        # I create and log in a user, and make a trade for testing
        self.user = User.objects.create_user(username="msguser", password="pass")
        self.client.login(username="msguser", password="pass")

        self.trade = Trade.objects.create(
            user=self.user,
            instrument="MSG",
            position_size=1,
            entry_price=1,
            entry_date=date(2025, 1, 1),
            outcome="open",
        )

    def _get_messages(self, response):
        """Helper to extract flash messages from the response."""
        return [m.message for m in response.context["messages"]]

    def test_create_shows_success_message(self):
        """After creating a trade, I see the success flash message."""
        url = reverse("add_trade")
        data = {
            "instrument": "NEW",
            "position_size": "2.5",
            "entry_price": "20",
            "exit_price": "22",
            "entry_date": "2025-03-01",
            "exit_date": "2025-03-02",
            "outcome": "win",
            "notes": "Created via test",
        }
        response = self.client.post(url, data, follow=True)
        msgs = self._get_messages(response)
        self.assertTrue(any("Trade successfully added." in m for m in msgs))

    def test_edit_shows_success_message(self):
        """Editing a trade triggers the 'updated successfully' message."""
        url = reverse("edit_trade", args=[self.trade.pk])
        data = {
            "instrument": "MSG-EDITED",
            "position_size": self.trade.position_size,
            "entry_price": self.trade.entry_price,
            "exit_price": self.trade.exit_price or "",
            "entry_date": self.trade.entry_date,
            "exit_date": self.trade.exit_date or "",
            "outcome": self.trade.outcome,
            "notes": "Edited via test",
        }
        response = self.client.post(url, data, follow=True)
        msgs = self._get_messages(response)
        self.assertTrue(any("Trade updated successfully." in m for m in msgs))

    def test_delete_shows_success_message(self):
        """Deleting a trade should show the 'deleted' flash message."""
        url = reverse("delete_trade", args=[self.trade.pk])
        response = self.client.post(url, follow=True)
        msgs = self._get_messages(response)
        self.assertTrue(any("Trade deleted." in m for m in msgs))

    def test_undo_delete_shows_success_message(self):
        """Undoing a delete should show the 'restored' flash message."""
        # Delete first
        self.client.post(reverse("delete_trade", args=[self.trade.pk]), follow=True)
        # Then undo
        response = self.client.get(reverse("undo_delete_trade"), follow=True)
        msgs = self._get_messages(response)
        # The test message text might be: "Deletion undone. Trade restored."
        self.assertTrue(any("restored" in m.lower() for m in msgs))

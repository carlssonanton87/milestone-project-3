from django.db import models
from django.contrib.auth.models import User


# Trade model: This represents a single trade that a user logs in their journal.
class Trade(models.Model):
    # The user who created the trade. If the user is deleted, their trades are also deleted.
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Name of the instrument traded (e.g., 'AAPL', 'EURUSD', etc.).
    instrument = models.CharField(max_length=100)

    # Position size (number of shares, contracts, etc.).
    position_size = models.DecimalField(max_digits=10, decimal_places=2)

    # Price at which the position was opened.
    entry_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Price at which the position was closed. Can be blank if the trade is still open.
    exit_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Date when the position was opened.
    entry_date = models.DateField()

    # Date when the position was closed. Can be blank if the trade is still open.
    exit_date = models.DateField(null=True, blank=True)

    # The result of the trade. Choices are 'win', 'loss', or 'open' (if still running).
    outcome = models.CharField(
        max_length=10, choices=[("win", "Win"), ("loss", "Loss"), ("open", "Open")]
    )

    # Optional notes field to allow users to reflect on the trade.
    notes = models.TextField(blank=True)

    # Calculate holding time in days. Returns None if trade isn't closed.
    def holding_days(self):
        if self.exit_date:
            return (self.exit_date - self.entry_date).days
        return None

    # Calculate the return (%) for the trade. Only valid for closed trades.
    def return_percent(self):
        if self.exit_price:
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        return None

    # String representation: helps identify each trade easily in the admin and elsewhere.
    def __str__(self):
        return f"{self.instrument} - {self.entry_date}"

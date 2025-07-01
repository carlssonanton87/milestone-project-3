from django.db import models
from django.contrib.auth.models import User

class Trade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    instrument = models.CharField(max_length=100)
    position_size = models.DecimalField(max_digits=10, decimal_places=2)
    entry_price = models.DecimalField(max_digits=10, decimal_places=2)
    exit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    entry_date = models.DateField()
    exit_date = models.DateField(null=True, blank=True)
    outcome = models.CharField(max_length=10, choices=[('win', 'Win'), ('loss', 'Loss'), ('open', 'Open')])
    notes = models.TextField(blank=True)

    def holding_days(self):
        if self.exit_date:
            return (self.exit_date - self.entry_date).days
        return None

    def return_percent(self):
        if self.exit_price:
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        return None

    def __str__(self):
        return f"{self.instrument} - {self.entry_date}"

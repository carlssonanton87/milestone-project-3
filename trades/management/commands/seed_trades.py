from django.core.management.base import BaseCommand
from trades.models import Trade
from django.contrib.auth.models import User
from datetime import timedelta, date
import random


class Command(BaseCommand):
    help = "Seed the database with 20 sample trades"

    def handle(self, *args, **kwargs):
        user = User.objects.first()
        if not user:
            self.stdout.write(
                self.style.ERROR("No user found. Create a superuser first.")
            )
            return

        Trade.objects.filter(user=user).delete()  # Optional: clear old data

        total_trades = 20
        open_trades = 5
        closed_trades = total_trades - open_trades
        win_trades = int(closed_trades * 0.9)

        outcomes = (
            (["win"] * win_trades)
            + (["loss"] * (closed_trades - win_trades))
            + (["open"] * open_trades)
        )
        random.shuffle(outcomes)

        for i in range(total_trades):
            outcome = outcomes[i]
            entry = date.today() - timedelta(days=random.randint(1, 5))
            instrument = f"TEST{i+1}"
            entry_price = random.uniform(100, 200)

            if outcome == "open":
                trade = Trade(
                    user=user,
                    instrument=instrument,
                    entry_date=entry,
                    entry_price=entry_price,
                    position_size=random.randint(1, 10),
                    outcome="open",
                    notes="Sample open trade",
                )
            else:
                holding_days = 2  # fixed average
                exit = entry + timedelta(days=holding_days)
                return_pct = random.uniform(8, 12)  # around 10%
                exit_price = (
                    entry_price * (1 + return_pct / 100)
                    if outcome == "win"
                    else entry_price * (1 - return_pct / 100)
                )

                trade = Trade(
                    user=user,
                    instrument=instrument,
                    entry_date=entry,
                    exit_date=exit,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    position_size=random.randint(1, 10),
                    outcome=outcome,
                    notes="Sample closed trade",
                )

            trade.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded {total_trades} trades for user: {user.username}"
            )
        )

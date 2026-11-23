import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from market.models import Instrument, InstrumentType, Portfolio, PriceHistory, Trade
from market.service import StockMatrketService


def random_price():
    return Decimal(random.randint(1000, 1000000)) / 100

class Command(BaseCommand):
    @transaction.atomic  
    def handle(self, *args, **options):
        fake = Faker("ru_RU")
        now = timezone.now()
        types = list(InstrumentType.objects.all())

        existing = set(Instrument.objects.values_list("ticker", flat=True))
        tickers = set()
        while len(tickers) < 1000:
            ticker = fake.lexify("????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            if ticker not in existing:
                tickers.add(ticker)

        instruments = []
        for ticker in tickers:
            price = random_price()
            instrument = Instrument.objects.create(
                ticker=ticker,
                name=fake.company(),
                instrument_type=random.choice(types),
                current_price=price,  
            )
            instruments.append(instrument)
            for day in range(1, 31):
                price = (price * Decimal(random.randint(95, 105)) / 100).quantize(Decimal("0.01"))
                record = PriceHistory.objects.create(instrument=instrument, price=price)
                PriceHistory.objects.filter(pk=record.pk).update(timestamp=now - timedelta(days=day))

        for _ in range(100):
            user = User.objects.create_user(
                username=f"{fake.unique.user_name()}",
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password="123",
            )
            for n in range(10):
                portfolio = Portfolio.objects.create(
                    user=user,
                    name=f"Портфель {n + 1}",
                    balance=random.randint(1000000, 5000000),
                )
                for instrument in random.sample(instruments, k=random.randint(1, 3)):
                    trade = Trade.objects.create(
                        portfolio=portfolio,
                        instrument=instrument,
                        order_type=Trade.OrderType.buy,
                        execution_type=Trade.ExecutionType.market,
                        quantity=random.randint(1, 10),
                    )
                    StockMatrketService.execute_trade(trade)
                    date = now - timedelta(days=random.randint(0, 30))
                    Trade.objects.filter(pk=trade.pk).update(created_at=date, executed_at=date)
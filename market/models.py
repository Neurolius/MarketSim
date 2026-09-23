from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username if self.user else f"Profile {self.id}"

@receiver(post_save, sender=User)
def on_user_create(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class InstrumentType(models.Model):
    name = models.TextField("Название типа инструмента", unique=True)

    class Meta:
        verbose_name = "Тип инструмента"
        verbose_name_plural = "Типы инструментов"

    def __str__(self):
        return self.name

class Instrument(models.Model):
    ticker = models.TextField("Тикер", unique=True)
    name = models.TextField("Название")
    instrument_type = models.ForeignKey(InstrumentType, on_delete=models.CASCADE, verbose_name="Тип инструмента")
    current_price = models.DecimalField("Текущая цена", max_digits=15, decimal_places=4, default=0)
    logo = models.ImageField("Логотип", upload_to="instrument_logos/", blank=True, null=True)

    class Meta:
        verbose_name = "Инструмент"
        verbose_name_plural = "Инструменты"

    def __str__(self):
        return self.ticker

class Portfolio(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="portfolios", verbose_name="Владелец портфеля")
    name = models.TextField("Название")
    balance = models.DecimalField("Баланс", max_digits=15, decimal_places=2, default=0)
    cover_image = models.ImageField("Обложка", upload_to="portfolio_covers/", blank=True, null=True)

    class Meta:
        verbose_name = "Портфель"
        verbose_name_plural = "Портфели"

    def __str__(self):
        return f"{self.name} ({self.user})"


class Position(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="positions", verbose_name="Портфель")
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, verbose_name="Инструмент")
    quantity = models.DecimalField("Количество", max_digits=15, decimal_places=4, default=0)
    average_price = models.DecimalField("Средняя цена", max_digits=15, decimal_places=4, default=0)

    class Meta:
        verbose_name = "Позиция"
        verbose_name_plural = "Позиции"

    def __str__(self):
        return f"{self.portfolio} — {self.instrument}"


class PriceHistory(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="price_history", verbose_name="Инструмент")
    price = models.DecimalField("Цена", max_digits=15, decimal_places=4)
    timestamp = models.DateTimeField("Временная метка", auto_now_add=True)

    class Meta:
        verbose_name = "История цен"
        verbose_name_plural = "Истории цен"

    def __str__(self):
        return f"{self.instrument} — {self.price} — {self.timestamp}"

class Trade(models.Model):
    class OrderType(models.TextChoices):
        buy = "buy", "Buy"
        sell = "sell", "Sell"

    class ExecutionType(models.TextChoices):
        market = "market", "Market"
        limit = "limit", "Limit"

    class Status(models.TextChoices):
        pending = "pending", "Pending"
        executed = "executed", "Executed"
        cancelled = "cancelled", "Cancelled"

    class Meta:
        verbose_name = "Сделка"
        verbose_name_plural = "Сделки"

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='trades', verbose_name='Портфель')
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, verbose_name='Инструмент')
    order_type = models.TextField("Тип заказа", choices=OrderType.choices)
    execution_type = models.TextField("Тип исполнения", choices=ExecutionType.choices)
    quantity = models.DecimalField("Количество", max_digits=15, decimal_places=4)
    price = models.DecimalField("Цена", max_digits=15, decimal_places=4, blank=True, null=True)
    status = models.TextField("Статус", choices=Status.choices, default=Status.pending)
    execution_price = models.DecimalField("Цена исполнения", max_digits=15, decimal_places=4, blank=True, null=True)
    created_at = models.DateTimeField("Создано в", auto_now_add=True)
    executed_at = models.DateTimeField("Исполнено в", blank=True, null=True)
    image = models.ImageField("Изображение", upload_to='trade_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.order_type} {self.quantity} {self.instrument} ({self.status})"

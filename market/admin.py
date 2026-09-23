from django.contrib import admin

from market.models import InstrumentType, Instrument, Portfolio, Position, PriceHistory, Trade, Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

@admin.register(InstrumentType)
class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticker', 'name', 'instrument_type', 'current_price')

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'balance')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'portfolio', 'instrument', 'quantity', 'average_price')

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'instrument', 'price', 'timestamp')

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'portfolio', 'instrument', 'order_type', 'status', 'quantity', 'execution_price', 'created_at')
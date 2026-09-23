from rest_framework import serializers
from market.models import InstrumentType, Instrument, Portfolio, Position, PriceHistory, Trade, Profile


class InstrumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentType
        fields = ['id', 'name']


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = ['id', 'ticker', 'name', 'instrument_type', 'current_price', 'logo']
        read_only_fields = ['current_price']


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'user', 'balance', 'cover_image']
        read_only_fields = ['balance']


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'portfolio', 'instrument', 'quantity', 'average_price']
        read_only_fields = ['portfolio', 'instrument', 'quantity', 'average_price']


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['id', 'instrument', 'price', 'timestamp']
        read_only_fields = ['instrument', 'price', 'timestamp']


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = ['id', 'portfolio', 'instrument', 'order_type', 'execution_type',
                    'quantity', 'price', 'status', 'execution_price',
                    'created_at', 'executed_at', 'image']
        read_only_fields = ['execution_price', 'status', 'created_at', 'executed_at']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user']
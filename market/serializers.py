from rest_framework import serializers
from market.models import InstrumentType, Instrument, Portfolio, Position, PriceHistory, Trade


class InstrumentTypeSerializer(serializers.ModelSerializer):
    instruments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = InstrumentType
        fields = ['id', 'name', 'instruments_count']

class InstrumentSerializer(serializers.ModelSerializer):
    prev_price = serializers.DecimalField(max_digits=15, decimal_places=4, read_only=True, allow_null=True)
    price_updated_at = serializers.DateTimeField(read_only=True, allow_null=True)
    
    class Meta:
        model = Instrument
        fields = ['id', 'ticker', 'name', 'instrument_type', 'current_price', 'logo', 'prev_price', 'price_updated_at']


class PortfolioSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('balance', None)
        return super().update(instance, validated_data)

    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("Баланс не может быть отрицательным")
        return value

    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'user', 'user_name', 'balance', 'cover_image']
        read_only_fields = ['user']


class PositionSerializer(serializers.ModelSerializer):
    instrument_info = InstrumentSerializer(source='instrument', read_only=True)

    class Meta:
        model = Position
        fields = ['id', 'portfolio', 'instrument', 'instrument_info', 'quantity', 'average_price']
        read_only_fields = ['portfolio', 'instrument', 'quantity', 'average_price']


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['id', 'instrument', 'price', 'timestamp']
        read_only_fields = ['instrument', 'price', 'timestamp']


class TradeSerializer(serializers.ModelSerializer):
    instrument_info = InstrumentSerializer(source='instrument', read_only=True)

    class Meta:
        model = Trade
        fields = ['id', 'portfolio', 'instrument', 'instrument_info', 'order_type',
                  'execution_type', 'quantity', 'price', 'status',
                  'execution_price', 'created_at', 'executed_at', 'image']
        read_only_fields = ['execution_price', 'status', 'created_at', 'executed_at']

    def validate(self, data):
        request = self.context.get('request')
        if request and data['portfolio'].user_id != request.user.id:
            raise serializers.ValidationError({'portfolio': 'Это портфель другого пользователя.'})
        if data['quantity'] <= 0:
            raise serializers.ValidationError({'quantity': 'Количество должно быть положительным числом.'})
        if data['execution_type'] == Trade.ExecutionType.limit:
            if not data.get('price') or data['price'] <= 0:
                raise serializers.ValidationError({'price': 'Укажите положительную цену для лимитного заказа.'})
        else:
            data['price'] = None
        return data

class TradeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = ['quantity', 'price', 'image']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Количество должно быть больше нуля')
        return value

    def validate_price(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError('Укажите положительную лимитную цену')
        return value